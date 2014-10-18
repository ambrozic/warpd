# -*- coding: utf-8 -*-
"""
"""

import time


class DB(object):
    """
    DB layer
    """

    def __init__(self):
        """
        """
        self.storage = {
            "name:example-throttle": {
                "interval": Throttle.DEF_INTERVAL,
                "sleep": Throttle.DEF_SLEEP * 100,
            },
        }

    def get(self, name, default=None):
        """
        :param name: name of throttle
        :param default: default return value
        :return: complete dict of state or default value
        """
        return self.storage.get(name, default)


    def save(self, name, entry):
        """
        :param name: name of throttle
        :param entry: value, complete dict of state
        :return: None
        """
        self.storage[name] = entry


class Throttle(object):
    """
    Cruise control class
    """

    DEF_NAME = "default"
    DEF_SLEEP = 0.001
    DEF_INTERVAL = 1000
    DEF_MAX_RPS = 0

    def __init__(
            self,
            name=None,
            sleep=None,
            interval=None,
            max_rps=None,
            calculate=None,
            db=None,
    ):
        """
        :param name: throttle name, used for storage
        :param sleep: sleep value
        :param interval: storage update interval
        :param max_rps: limit requests / second
        :param calculate: method to calculate sleep value
        :return:
        """
        self.updates = 0
        self.sum_updates = 0
        self.date_last_modified = None

        self.db = db or DB()
        self.name = name or self.DEF_NAME

        if sleep is None:
            sleep = self.db.get(self.name, {}).get("sleep", self.DEF_SLEEP)

        if interval is None:
            interval = self.db.get(self.name, {}).get("interval", self.DEF_INTERVAL)
        self.interval = int(interval)

        if max_rps is None:
            max_rps = self.db.get(self.name, {}).get("max_rps", self.DEF_MAX_RPS)
        self.max_rps = int(max_rps)

        self.custom_calculate = calculate

        self.state = State(
            sleep=float(sleep),
            interval=int(self.interval),
            max_rps=int(self.max_rps),
        )

    def __enter__(self):
        """
        start context
        """
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        finalize context
        """
        self.update()
        if exc_type is not None:
            pass

    @property
    def sleep(self):
        """
        :return: sleep value
        """
        self.calculate()
        self.update()
        return self.state.sleep

    def update(self):
        """
        keep track of updates and state in storage
        """
        self.updates += 1
        self.sum_updates += 1
        self.state._updates = self.sum_updates
        if self.updates >= self.interval:
            self.db.save(
                name=self.name,
                entry=dict(
                    sleep=self.state.sleep,
                    delta=self.state.delta,
                    rps=self.state.rps,
                    interval=self.interval,
                    max_rps=self.max_rps,
                    updates=self.state.updates,
                )
            )
            self.updates = 0

    def calculate(self):
        """
        calculate next sleep value
        """
        now = time.time()
        diff = None

        if self.date_last_modified:
            diff = now - self.date_last_modified or 1e-4
            self.state._rps = 1.0 / diff
            self.state._delta = diff - self.state.sleep
        self.date_last_modified = now

        # no diff, no calculation
        if not diff:
            return

        # if 'max_rps' is set, custom sleep value calculation is ignored
        if self.max_rps:
            self.state._sleep = (1.0 / (diff / self.state.sleep)) / float(self.max_rps)
            return

        # calculate sleep value using passed custom_calculate method
        if self.custom_calculate:
            self.state._sleep = self.custom_calculate(self.state)


class State(object):
    """
    State representation of Throttle class
    """

    def __init__(self, sleep, interval, max_rps):
        self._sleep = sleep
        self._interval = interval
        self._delta = 0.0
        self._max_rps = max_rps
        self._rps = 0.0
        self._updates = 0.0

    @property
    def sleep(self):
        return self._sleep

    @property
    def interval(self):
        return self._interval

    @property
    def delta(self):
        return self._delta

    @property
    def max_rps(self):
        return self._max_rps

    @property
    def rps(self):
        return self._rps

    @property
    def updates(self):
        return self._updates


throttle = Throttle
