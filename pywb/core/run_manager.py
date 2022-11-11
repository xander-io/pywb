from threading import ThreadError, Thread
from typing import List, Dict

from pywb.core.logger import logger
from pywb.core.runner import RunConfig, Runner
from pywb.core.action import Action
from pywb.core.plugin import Plugin
from pywb.web.browser import _Browser


class RunManager(Thread):
    def __init__(self, actions: List[Action], plugins: Dict[str, Plugin], browser: _Browser, default_run_cfg: RunConfig) -> None:
        super().__init__()
        self.__default_run_cfg = default_run_cfg
        self.__actions = actions
        self.__runners = []
        self.__plugins = plugins
        self.__browser = browser
        self.__shut_down = False

    def run(self):
        self.__delegate_and_wait()

    def __delegate_and_wait(self) -> None:
        self.__actions_to_runners()
        self.__start_runners()
        # Waiting for runners to finish executing
        self.__wait_for_runners()

    def __start_runners(self) -> None:
        [runner.start() for runner in self.__runners]

    def __actions_to_runners(self) -> None:
        # Merge actions into plugins - One plugin instance for multiple actions
        for action in self.__actions:
            if action.plugin_name not in self.__plugins:
                raise ValueError(
                    "Unable to find plugin %s from loaded external plugins" % action.plugin_name)

            # Create a new run config with the action
            new_cfg = RunConfig.from_run_config(self.__default_run_cfg)
            new_cfg.actions = [action]
            # Add a new runner with the config and plugin
            self.__runners.append(Runner(self.__plugins[action.plugin_name], self.__browser, new_cfg))

    def __wait_for_runners(self) -> None:
        runner_timeout = 60 * 5
        rogue_plugin = False
        # Wait for timeout in secs for each runner to finish cleaning up properly
        for runner in self.__runners:
            attempts = 0
            while runner.is_alive():
                runner.join(timeout=1)
                # If we get an external shutdown, start tracking with a timeout
                if self.__shut_down:
                    if attempts < runner_timeout:
                        attempts += 1
                    else:
                        # Plugin isn't playing nicely... We'll try to clean up the rest
                        rogue_plugin = True
                        break
        if rogue_plugin:
            logger.error("One or more plugins did not clean up properly... Forcing thread exit!")
        logger.info("Runners have completed execution... tearing down")

    def shut_down(self) -> None:
        # Signal shut_down for each runner
        for runner in self.__runners:
            runner.shut_down()

        # Wait for runners to finish execution
        self.__shut_down = True
