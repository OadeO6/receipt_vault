import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import CurrentMessage, Retries, TimeLimit, ShutdownNotifications


broker = RedisBroker(host="redis")
broker.add_middleware(CurrentMessage())
broker.add_middleware(Retries(max_retries=3))
broker.add_middleware(TimeLimit(time_limit=1000 * 60 * 5)) #5 min

broker.add_middleware(ShutdownNotifications())
