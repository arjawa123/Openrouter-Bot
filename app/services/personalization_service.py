from sqlalchemy.ext.asyncio import AsyncSession
from app.db import crud
from app.db.models import User

class PersonalizationService:
    async def get_or_create_profile(self, db: AsyncSession, tg_user) -> User:
        user = await crud.get_user_by_telegram_id(db, tg_user.telegram_user_id if hasattr(tg_user, 'telegram_user_id') else tg_user.id)
        if not user:
            user = await crud.create_user(
                db, 
                telegram_id=tg_user.id, 
                username=tg_user.username,
                first_name=tg_user.first_name
            )
        return user

    async def update_profile(self, db: AsyncSession, user_id: int, **kwargs) -> User:
        return await crud.update_user(db, user_id, kwargs)

personalization_service = PersonalizationService()
