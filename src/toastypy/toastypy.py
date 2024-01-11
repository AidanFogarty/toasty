import functools
import logging

logger = logging.getLogger(__name__)


def toasty(func):
    @functools.wraps(func)
    def wrapper(event, context):
        if event.get("type") == "toasty":
            logger.info({"message": "toasty warming lambda", "event": event})
            return

        logger.info({"message": "toasty real invocation"})
        return func(event, context)

    return wrapper
