from multiprocessing.sharedctypes import Value
from threading import ThreadError
from pywb import ENVIRON_DEBUG_KEY
from pywb.core.logger import logger
from pywb.core.runner import RunConfig, Runner
from pywb.surfing.chrome import Chrome


class RunManager(object):

    def __init__(self, run_cfg) -> None:
        self._common_run_cfg = run_cfg
        self._runners = []
        self._shutdown = False

    def delegate_and_wait(self, actions, plugins) -> None:
        self._actions_to_runners(actions, plugins)
        self._start_runners()

        # Waiting for runners to finish executing
        self._wait_for_runners()
        logger.info("Runners have completed execution... tearing down")

    def _start_runners(self) -> None:
        for runner in self._runners:
            runner.start()

    def _actions_to_runners(self, actions, plugins) -> None:
        runs = {}

        # Merge actions into plugins - One plugin instance for multiple actions
        for action in actions:
            if action.plugin not in plugins:
                raise ValueError(
                    "Unable to find plugin %s from loaded external plugins" % action.plugin)

            if action.plugin not in runs:
                # Create a new run config with the action
                new_cfg = RunConfig.from_run_config(self._common_run_cfg)
                new_cfg.actions = [action]
                # Add the action to existing run configs
                runs[action.plugin] = (plugins[action.plugin], new_cfg)
            else:
                # Append action to existing run config
                _, cfg = runs[action.plugin]
                cfg.actions.append(action)

        # Create runners
        self._runners = [Runner(plugin, run_cfg)
                         for _, (plugin, run_cfg) in runs.items()]

    def _wait_for_runners(self, timeout=None) -> None:
        rogue_plugin = False
        # Wait for timeout in secs for each runner to finish cleaning up properly
        for runner in self._runners:
            attempts = 0
            while runner.is_alive() and not self._shutdown:
                runner.join(timeout=1)
                if timeout:
                    if attempts < timeout:
                        attempts += 1
                    else:
                        # Plugin isn't playing nicely... We'll try to clean up the rest
                        rogue_plugin = True
                        break
        if rogue_plugin:
            raise ThreadError(
                "One or more plugins did not clean up properly... Forcing process exit!")

    def shut_down(self) -> None:
        # Signal shutdown for each runner
        for runner in self._runners:
            runner.shut_down()

        # Wait for runners to finish execution
        self._wait_for_runners(timeout=10)
        self._shutdown = True
