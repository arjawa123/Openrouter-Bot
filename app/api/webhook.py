from fastapi import APIRouter, Request, Header, HTTPException
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from loguru import logger
from app.config import settings

router = APIRouter()

@router.post("/webhook")
async def telegram_webhook(
    request: Request, 
    x_telegram_bot_api_secret_token: str = Header(None)
):
    # Verify Secret Token if set
    secret = settings.telegram_webhook_secret.get_secret_value()
    if secret and x_telegram_bot_api_secret_token != secret:
        logger.warning("Invalid webhook secret token")
        raise HTTPException(status_code=401, detail="Invalid secret token")
        
    bot: Bot = request.app.state.bot
    dp: Dispatcher = request.app.state.dp
    
    try:
        data = await request.json()
        update = Update(**data)
        await dp.feed_update(bot=bot, update=update)
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
    
    return {"status": "ok"}
