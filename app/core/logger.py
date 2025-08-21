import logging
from asgi_correlation_id.log_filters import CorrelationIdFilter
from magic.loader import sys


log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    'filters': {
        "correlation_id": {
            "()": CorrelationIdFilter,
            "uuid_length": 32
        }
    },
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(correlation_id)s]",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s [%(correlation_id)s]",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "json": {
            "format": '{"timestamp": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s", "file": "%(filename)s", "line": %(lineno)d, "correlation_id": "%(correlation_id)s"}',
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "filters": ["correlation_id"],
            "stream": sys.stdout
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            # "formatter": "detailed",
            "formatter": "json",
            "filename": "app.log",
            "maxBytes": 10485760,  # 10MB
             "filters": ["correlation_id"],
            "backupCount": 5
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "detailed",
            "filename": "errors.log",
            "maxBytes": 10485760,
            "backupCount": 5,
            "filters": ["correlation_id"],
            "level": "ERROR"
        }
    },
    "loggers": {
        "": {
             "handlers": ["console", "file"],
             "level": "INFO",
             "propagate": False
             },
        "app": {
                "handlers": ["console", "file", "error_file"],
                "level": "DEBUG",
                "propagate": False
                },
        "uvicorn": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False
        },
        "sqlalchemy.engine": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False
        }
    }
}

class CustomLogger:
    reserved_params = ['exc_info', 'stack_info', 'stacklevel']
    def __init__(self, name: str = __name__):
        self.logger = logging.getLogger(name)

    # def _get_extra_contex(self, correlation_id: uuid.UUID = Depends(get_correlation_id)):
    #     return correlation_id

    def error(self, message, **extra):
        exc_info = extra.get("exc_info", None)
        for param in self.reserved_params:
            extra.pop(param, None)
        self.logger.error(message, exc_info=exc_info, extra=extra)

    def warning(self, message, **extra):
        for param in self.reserved_params:
            extra.pop(param, None)
        self.logger.warning(message, extra=extra)

    def debug(self, message, **extra):
        for param in self.reserved_params:
            extra.pop(param, None)
        self.logger.debug(message, extra=extra)

    def info(self, message, **extra):
        for param in self.reserved_params:
            extra.pop(param, None)
        # self.logger.info("Info message", extra={"user": "johndoe", "session_id": "abc123"})
        self.logger.info(message, extra=extra)
