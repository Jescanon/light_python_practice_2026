import logging

from src.config import LOG_PATH

def setup_logging(verbose: bool = False, vverbose: bool = False):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    handlers = [logging.FileHandler(LOG_PATH, encoding="utf-8")]
    if verbose or vverbose:
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG if vverbose else logging.INFO)
        handlers.append(console)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
        handlers=handlers,
    )
