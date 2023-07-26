from typing import Dict, Any
from aiogram.utils.i18n import I18nMiddleware
from aiogram.types import TelegramObject
from bot.mongodb.filters import get_language



class MyI18nMiddleware(I18nMiddleware):
    async def get_locale(self, event: TelegramObject, data: Dict[str, Any]) -> str:
        user_language = await get_language()
        if not user_language:
            user_language = data['event_from_user'].language_code
            if user_language == 'uk':
                user_language = 'ua'
        else:
            user_language = user_language['language']
        return user_language
