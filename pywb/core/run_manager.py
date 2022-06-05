from threading import ThreadError
from pywb.core.runner import RunConfig, Runner


class RunManager(object):

    def __init__(self, run_cfg) -> None:
        self._common_run_cfg = run_cfg
        self._runners = []
        self._shutdown = False

    def delegate_and_wait(self, actions, plugins) -> None:
        # TODO: Delegate tasking to Runners
        # Chrome(headless=(ENVIRON_DEBUG_KEY not in environ)
        run_cfg = RunConfig.copy(self._common_run_cfg)
        x = Runner()
        x.start()
        self._runners.append(x)

        # Waiting for runners
        self._wait_for_runners()
        print("MANAGER OUT!")

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
