from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

language_menu = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="en")
    ],
])

delete_me = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="❌ Закрыть", callback_data="delete_me")
    ]
])
