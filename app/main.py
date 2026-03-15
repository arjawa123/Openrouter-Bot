from contextlib import asynccontextmanager
from fastapi import FastAPI
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from app.config import settings
from app.logging_config import setup_logging
from app.api import health, webhook
from app.bot import commands, handlers
from loguru import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Starting Telegram OpenRouter Bot...")
    
    # Initialize Bot and Dispatcher
    bot_token = settings.telegram_bot_token.get_secret_value()
    bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode="Markdown"))
    dp = Dispatcher()
    
    # Register routers
    dp.include_router(commands.router)
    dp.include_router(handlers.router)
    
    app.state.bot = bot
    app.state.dp = dp
    
    # Set Webhook
    if settings.app_env != "development" and settings.telegram_webhook_url:
        webhook_url = f"{settings.telegram_webhook_url}/webhook"
        secret = settings.telegram_webhook_secret.get_secret_value() if settings.telegram_webhook_secret else None
        await bot.set_webhook(url=webhook_url, secret_token=secret)
        logger.info(f"Webhook set to {webhook_url}")
    else:
        logger.info("Running in development mode or no webhook URL provided. Consider using ngrok for local webhook testing.")
        
    yield
    
    logger.info("Shutting down...")
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.session.close()

app = FastAPI(title=settings.app_name, lifespan=lifespan)

# Include API Routers
app.include_router(health.router)
app.include_router(webhook.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.app_host, port=settings.app_port, reload=True)
