from copy import deepcopy
from enum import Enum
from threading import Thread
from typing import Dict, List

from cmd2.table_creator import Column, SimpleTable

from pywb.core.logger import logger
from pywb.core.plugin.plugin import Plugin
from pywb.core.run.action import Action
from pywb.core.run.runner import RunConfig, Runner
from pywb.web.browser import _Browser


class RunManagerStatus(Enum):
    NOT_STARTED = 0
    STOPPED = 1
    SHUTTING_DOWN = 2
    STARTED = 3
    RUNNING = 4

    def __gt__(self, other: object):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def __ge__(self, other: object):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented

    def __lt__(self, other: object):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented

    def __le__(self, other: object):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented


class RunManager(Thread):
    def __init__(self, actions: List[Action] = None, plugins: Dict[str, Plugin] = None,
                 browser: _Browser = None, run_cfg: RunConfig = None) -> None:
        super().__init__()
        self.run_cfg = run_cfg
        self.__actions = actions
        self.__runners = []
        self.__plugins = plugins
        self.__browser = browser
        self.__shut_down = False
        self.status = RunManagerStatus.NOT_STARTED

    def run(self):
        assert (self.__actions and self.__plugins
                and self.__browser and self.run_cfg), "Critical Error - RunManager did not get initialized properly"
        self.status = RunManagerStatus.STARTED
        self.__delegate_and_wait()

    def __delegate_and_wait(self) -> None:
        self.__actions_to_runners()
        self.__start_runners()
        self.status = RunManagerStatus.RUNNING
        # Waiting for runners to finish executing
        self.__wait_for_runners()

    def __start_runners(self) -> None:
        [runner.start() for runner in self.__runners]

    def __actions_to_runners(self) -> None:
        # Merge actions into plugins - One plugin instance for multiple actions
        for action in self.__actions:
            if action.plugin_name not in self.__plugins:
                logger.warning(
                    "Unable to find plugin %s from loaded external plugins... Skipping" % action.plugin_name)
                continue

            # Create a new run config with the action
            new_cfg = deepcopy(self.run_cfg)
            new_cfg.action = deepcopy(action)
            # Add a new runner with the config and plugin
            self.__runners.append(
                Runner(self.__plugins[action.plugin_name], self.__browser, new_cfg))

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
            logger.error(
                "One or more plugins did not clean up properly... Forcing thread exit!")
        logger.info("Runners have completed execution... tearing down")
        self.status = RunManagerStatus.STOPPED

    def shut_down(self) -> None:
        # Signal shut_down for each runner
        for runner in self.__runners:
            runner.shut_down()

        # Wait for runners to finish execution
        self.__shut_down = True
        self.status = RunManagerStatus.SHUTTING_DOWN

    def generate_status_table(self, extended=True) -> str:
        columns = [Column("Service", width=50), Column("Status", width=20)]
        status = [["Python Web Bot (pywb) Service", str(self.status.name)]]
        status_str = SimpleTable(columns).generate_table(status)

        runner_data = []
        runner_str = ""
        if extended:
            columns = [Column("Runner ID", width=15),
                       Column("Action", width=50), Column("Plugin", width=20)]
            for i in range(len(self.__runners)):
                runner = self.__runners[i]
                runner_data.append(
                    [i, "'%s'" % runner.action.title, str(runner.plugin)])

            if len(runner_data) > 0:
                runner_str = "\n\n\n%s\n\nTOTAL RUNNERS: (%s)" % (
                    SimpleTable(columns).generate_table(runner_data), len(runner_data))

        return ("\n%s%s\n\n" % (status_str, runner_str))
