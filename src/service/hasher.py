import logging
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)

def file_hash(path: Path) -> str:
    h = hashlib.blake2b()
    with open(path, "rb") as f:
        logger.debug("hashing %s", path)
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


