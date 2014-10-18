#warpd
Because sometimes even your best gravimetric field displacement manifold propulsion system needs cruise control.

##Install
Put some code somewhere.

##Examples

Simple iteration control. You really don't need this one.
```python
import time
import warpd

with warpd.throttle(sleep=0.2) as throttle:
    while True:
        # some of your code
        time.sleep(throttle.sleep)
```

Calculate iteration time.
```python
import time
import warpd

calculate = lambda obj: 0.002 if obj.delta > 1.0 else 0.001

with warpd.throttle(calculate=calculate) as throttle:
    while True:
        # some of your code
        time.sleep(throttle.sleep)
```

Limit maximum number of iterations per second.
```python
import time
import warpd

with warpd.throttle(max_rps=800) as throttle:
    while True:
        # some of your code
        time.sleep(throttle.sleep)
```

Use redis as a storage.
```python
import time
import redis
import warpd


class RedisDB(warpd.DB):
    """
    Redis DB layer
    """

    def __init__(
            self,
            host="localhost",
            port=6379,
            db=0,
            password=None,
            socket_timeout=None,
            connection_pool=None,
            charset="utf-8",
            errors="strict",
            decode_responses=False,
            unix_socket_path=None,
            key_prefix="warpd:{0}",
    ):
        self.db = redis.StrictRedis(
            host=host,
            port=port,
            db=db,
            password=password,
            socket_timeout=socket_timeout,
            connection_pool=connection_pool,
            charset=charset,
            errors=errors,
            decode_responses=decode_responses,
            unix_socket_path=unix_socket_path
        )
        self.key_prefix = key_prefix

    def get(self, name, default=None):
        """
        :param name: name of throttle
        :param default: default return value
        :return: complete dict of state or default value
        """
        return self.db.hmgetall(name=self.key_prefix.format(name)) or default

    def save(self, name, entry):
        """
        :param name: name of throttle
        :param entry: value, complete dict of state
        :return:
        """
        if not isinstance(entry, (dict,)):
            raise Exception("'entry' should be dict")
        return self.db.hmset(name=self.key_prefix.format(name), mapping=entry)


with warpd.throttle(db=RedisDB(), interval=0.2, max_rps=800) as throttle:
    while True:
        # some of your code
        time.sleep(throttle.sleep)
```

Or create your own throttle using RedisDB from previous example.
```python

class RedisThrottle(warpd.throttle):
    def __init__(self, **kwargs):
        super(RedisThrottle, self).__init__(db=RedisDB(), **kwargs)


with RedisThrottle(interval=0.2, max_rps=800) as throttle:
    while True:
        # some of your code
        time.sleep(throttle.sleep)
```


Now imagine web interface controlling all your applications and collecting their current states.
