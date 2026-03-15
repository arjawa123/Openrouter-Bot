import sys
from loguru import logger
from app.config import settings

def setup_logging():
    logger.remove()
    
    log_level = settings.log_level.upper()
    
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
    )
    
    logger.info(f"Logging configured with level: {log_level}")
