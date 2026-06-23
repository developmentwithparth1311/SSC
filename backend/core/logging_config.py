"""Central logging setup."""
import logging

from core.config import LOG_LEVEL

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("ssc")
logger.info("Logging initialized (high priority observability)")