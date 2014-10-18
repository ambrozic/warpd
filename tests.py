# -*- coding: utf-8 -*-
"""
    warpd tests

    py.test -v tests.py
    py.test -v tests.py::test_method

"""

import warpd


def test_init():
    loops = 5
    name = "test-name"
    calculate = lambda obj: 0.002 if obj.delta > 1.0 else 0.001

    with warpd.throttle(name="name:example-throttle", interval=10) as throttle:
        for i in range(loops):
            assert throttle.db.storage["name:example-throttle"]["sleep"] == 0.1
            assert throttle.db.storage["name:example-throttle"]["interval"] == 1000
            throttle.sleep

    with warpd.throttle(name=name, interval=5) as throttle:
        for i in range(loops * 2):
            assert throttle.name == name
            if i >= 5:
                assert name in throttle.db.storage
            throttle.sleep

    with warpd.throttle(calculate=calculate) as throttle:
        for i in range(loops):
            assert throttle.interval == throttle.DEF_INTERVAL
            assert throttle.max_rps == throttle.DEF_MAX_RPS
            throttle.sleep


def test_interval():
    loops = 5
    interval = loops
    calculate = lambda obj: 0.002 if obj.delta > 1.0 else 0.001

    with warpd.throttle(calculate=calculate, interval=interval) as throttle:
        for i in range(loops * 2):
            if i >= interval:
                assert throttle.db.storage[throttle.DEF_NAME]["sleep"] == throttle.DEF_SLEEP
                assert throttle.db.storage[throttle.DEF_NAME]["interval"] == 5
                assert throttle.db.storage[throttle.DEF_NAME]["max_rps"] == throttle.DEF_MAX_RPS
            else:
                assert throttle.interval == interval
                assert throttle.max_rps == throttle.DEF_MAX_RPS
            throttle.sleep


def test_max_rps():
    loops = 5
    interval = loops
    max_rps = 100000
    calculate = lambda obj: 0.002 if obj.delta > 1.0 else 0.001

    with warpd.throttle(calculate=calculate, interval=interval, max_rps=max_rps) as throttle:
        for i in range(loops * 2):
            if i >= interval:
                assert throttle.db.storage[throttle.DEF_NAME]["sleep"] != throttle.DEF_SLEEP
                assert throttle.db.storage[throttle.DEF_NAME]["interval"] == interval
                assert throttle.db.storage[throttle.DEF_NAME]["max_rps"] == max_rps
            else:
                assert throttle.interval == interval
                assert throttle.max_rps == max_rps

            throttle.sleep


def test_calculate():
    loops = 5
    interval = loops
    max_rps = 1000000

    def calculate(obj):
        assert obj.interval == interval
        return obj.sleep

    with warpd.throttle(calculate=calculate, interval=interval) as throttle:
        for i in range(loops * 2):
            throttle.sleep

    # test when max_rps is set, calculate is ignored
    def calculate(obj):
        raise Exception("when max_rps is set, calculate is ignored")

    with warpd.throttle(calculate=calculate, max_rps=max_rps) as throttle:
        for i in range(loops * 2):
            throttle.sleep


def test_state():
    loops = 5
    interval = loops
    max_rps = 1000000

    with warpd.throttle() as throttle:
        for i in range(loops * 2):
            assert throttle.state.max_rps == throttle.DEF_MAX_RPS
            assert throttle.state.sleep == throttle.DEF_SLEEP
            assert throttle.state.interval == throttle.DEF_INTERVAL
            assert int(throttle.state.delta) == 0
            throttle.sleep

    with warpd.throttle(interval=interval) as throttle:
        for i in range(loops * 2):
            assert throttle.state.max_rps == throttle.DEF_MAX_RPS
            assert throttle.state.sleep == throttle.DEF_SLEEP
            assert throttle.state.interval == interval
            assert int(throttle.state.delta) == 0
            throttle.sleep

    with warpd.throttle(max_rps=max_rps) as throttle:
        for i in range(loops * 2):
            assert throttle.state.max_rps == max_rps
            assert throttle.state.interval == throttle.DEF_INTERVAL
            assert int(throttle.state.delta) == 0
            throttle.sleep


def test_database():
    class RedisDB(warpd.DB):
        def get(self, name, default=None):
            return dict(name=name, default=default)

        def save(self, name, entry):
            return dict(name=name, entry=entry)

    class RedisThrottle(warpd.throttle):
        def __init__(self, **kwargs):
            super(RedisThrottle, self).__init__(db=RedisDB(), **kwargs)

    interval = 12345
    max_rps = 1234512345

    with RedisThrottle(interval=interval) as throttle:
        assert isinstance(throttle.db, RedisDB)
        d = dict(name="NAME", default=list())
        assert throttle.db.get(**d) == d

        d = dict(name="NAME", entry=dict(a=1, b=1))
        assert throttle.db.save(**d) == d
        assert throttle.interval == interval
        assert throttle.max_rps == throttle.DEF_MAX_RPS

    with RedisThrottle(max_rps=max_rps) as throttle:
        assert isinstance(throttle.db, RedisDB)
        d = dict(name="NAME", default=list())
        assert throttle.db.get(**d) == d

        d = dict(name="NAME", entry=dict(a=1, b=1))
        assert throttle.db.save(**d) == d
        assert throttle.max_rps == max_rps
        assert throttle.interval == throttle.DEF_INTERVAL

    with RedisThrottle(calculate=lambda x: x * x) as throttle:
        assert isinstance(throttle.db, RedisDB)
        d = dict(name="NAME", default=list())
        assert throttle.db.get(**d) == d

        d = dict(name="NAME", entry=dict(a=1, b=1))
        assert throttle.db.save(**d) == d
        assert throttle.max_rps == throttle.DEF_MAX_RPS
        assert throttle.interval == throttle.DEF_INTERVAL
        assert throttle.custom_calculate(2) == 2 * 2
