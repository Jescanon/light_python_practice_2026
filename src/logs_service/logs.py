import logging

from src.config import LOG_PATH


def setup_logging(verbose=False):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    handlers = [logging.FileHandler(LOG_PATH, encoding="utf-8")]
    if verbose:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
        handlers=handlers,
    )
