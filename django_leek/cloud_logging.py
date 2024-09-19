import copy
import logging
import sys
from collections import deque
from contextlib import contextmanager
from typing import Any, Sequence, Union

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone
from google.cloud.logging_v2.handlers.structured_log import StructuredLogHandler

FORMAT = "%(message)s"
IMPORT_FORMAT = "[%(namespace)s] tenant:%(tenant_name)s| %(message)s"
UNSTRUCTURED_FORMAT = "%(asctime)s |%(threadName)-10s| %(filename)31s:%(lineno)-4d |%(levelname)7s| {message_format}"

LOGGING_CONTEXT_MANAGERS = dict()  # type: dict[str, LoggingContextHandler]


def get_logger(name: str) -> Any:
    if name not in LOGGING_CONTEXT_MANAGERS:
        logging_context_handler = LoggingContextHandler()
        context_filter = ImportContextFilter(logging_context_handler)

        logger = setup_logging(name=name, format=IMPORT_FORMAT)
        logger.addFilter(context_filter)

        LOGGING_CONTEXT_MANAGERS[name] = logging_context_handler
        return logger

    logger = logging.getLogger(name)
    return logger


class LoggingContextHandler:
    """Allows having a stack of logging context variables.
    Each time you add to the stack the logger will get new context variables.
    Each time you remove it will go to the ones it had previously.
    This allows stacking like:
    with logger_context(contextvars_1):
        log.info() -> log with contextvars_1

        with logger_context(contextvars_2):
            log.info() -> log with contextvars_2

        log.info() -> log with contextvars_1 again
    """

    def __init__(self):
        self.attributes = deque([{}])  # type: deque[dict]

    @property
    def current_attributes(self) -> dict:
        return self.attributes[0]

    def add(self, **new_context_vars) -> None:
        old_context = self.attributes[0]
        new_context = {**old_context, **new_context_vars}
        self.attributes.appendleft(new_context)

    def get(self, key: str, default: Any = None) -> Any:
        return self.attributes[0].get(key, default)

    def remove(self) -> None:
        self.attributes.popleft()

    def __str__(self) -> str:
        return str(self.attributes)


class ImportContextFilter(logging.Filter):
    def __init__(self, import_logging_context_handler: LoggingContextHandler):
        super(ImportContextFilter, self).__init__()
        self.import_logging_context_handler = import_logging_context_handler

    def filter(self, record: logging.LogRecord) -> bool:
        record.tenant_name = self.import_logging_context_handler.get("tenant_name")

        namespace_str = ">".join(
            self.import_logging_context_handler.get("namespace", [])
        )
        record.namespace = namespace_str.upper()
        record.json_fields = {
            **getattr(record, "json_fields", {}),
            "tenant_name": record.tenant_name,
            "namespace": record.namespace,
        }
        return True


class TimestampFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.json_fields = {
            **getattr(record, "json_fields", {}),
            "timestamp": str(timezone.now()),
        }
        return True


@contextmanager
def append_logger_context_namespace(logger: logging.Logger, namespace: str) -> None:
    logging_context_handler = LOGGING_CONTEXT_MANAGERS[logger.name]
    try:
        next_attributes = copy.deepcopy(logging_context_handler.current_attributes)
        current_namespace = next_attributes.get("namespace", [])
        next_attributes["namespace"] = current_namespace + [namespace]
        logging_context_handler.add(**next_attributes)
        yield
    finally:
        logging_context_handler.remove()


@contextmanager
def logger_context(
    logger: logging.Logger, namespace: Union[str, Sequence[str]], **kwargs
) -> None:
    logging_context_handler = LOGGING_CONTEXT_MANAGERS[logger.name]
    try:
        if isinstance(namespace, str):
            # convert namespace to sequence
            namespace = [namespace]
        logging_context_handler.add(namespace=namespace, **kwargs)
        yield
    finally:
        logging_context_handler.remove()


def _structured_log() -> bool:
    try:
        return settings.STRUCTURED_LOG
    except (ImproperlyConfigured, AttributeError):
        return False


def _get_handler(format: str) -> logging.StreamHandler:
    if _structured_log():
        log_handler: logging.StreamHandler = StructuredLogHandler(stream=sys.stderr)
        log_handler.setFormatter(logging.Formatter(FORMAT))
    else:
        log_handler = logging.StreamHandler(stream=sys.stderr)
        log_handler.setFormatter(
            logging.Formatter(UNSTRUCTURED_FORMAT.format(message_format=format))
        )
    return log_handler


def setup_logging(name: str, format: str) -> logging.Logger:
    """Sets up and returns the recommendation logger."""
    logger = logging.getLogger(name)
    logger.setLevel(
        logging.DEBUG
    )  # logger passes on everything, but the handler may filter
    logger.handlers = []
    log_handler = _get_handler(format)
    log_handler.setLevel(logging.INFO)
    logger.addHandler(log_handler)

    if _structured_log():
        logger.addFilter(TimestampFilter())

    return logger
