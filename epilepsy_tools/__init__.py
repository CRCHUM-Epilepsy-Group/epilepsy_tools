import logging

handler = logging.StreamHandler()

dt_fmt = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{"
)
logger = logging.getLogger(__name__)
handler.setFormatter(formatter)
logger.addHandler(handler)
