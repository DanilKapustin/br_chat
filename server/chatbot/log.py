from pydantic import BaseModel


class LogConfig(BaseModel):
    """Logging configuration"""

    LOGGER_NAME: str = "chatbot"
    LOG_FORMAT: str = (
        "%(asctime)s\t%(process)d\t%(thread)d\t%(name)-40s\t%(levelname)-8s%(message)s"
    )
    LOG_LEVEL: str = "DEBUG"

    # Logging config
    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    }
    loggers = {
        "": {"handlers": ["default"], "level": LOG_LEVEL},
        "atlassian": {"handlers": ["default"], "level": "INFO"},
        "pdfminer": {"handlers": ["default"], "level": "INFO"},
        "multipart": {"handlers": ["default"], "level": "INFO"},
    }
