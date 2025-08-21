from time import sleep
import dramatiq
from dramatiq.middleware import CurrentMessage, Shutdown
import requests

from app.core.broker import broker
from app.core.logger import CustomLogger

logger = CustomLogger(__name__)

dramatiq.set_broker(broker)


@dramatiq.actor(notify_shutdown=False)
def count_words(url):
    try:
        details = CurrentMessage.get_current_message()
        job_id = details.message_id
        response = requests.get(url)
        count = len(response.text.split(" "))

        print(f"r There are {count} words at {url!r}.")
        sleep(20)
        print('done')
    except Exception:
        print(6666)
        logger.warning(f"Stoping Job: 888 due to SIGTERM")


@dramatiq.actor
def example():
    try:
        print(CurrentMessage.get_current_message().__dir__())
    except Exception:
        print(5555)
        raise
