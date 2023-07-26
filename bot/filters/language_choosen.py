from aiogram.filters import BaseFilter

from bot.mongodb.filters import language_choosen


class LanguageChoosen(BaseFilter):
    async def __call__(self, message, state):
        return await language_choosen()

class LanguageNotChoosen(BaseFilter):
    async def __call__(self, message, state):
        return not await language_choosen()