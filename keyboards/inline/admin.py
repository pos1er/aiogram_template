from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🔎 Сервис", callback_data="service")
    ],
    [
        InlineKeyboardButton(text="🎁 Промокод", callback_data="promo_code")
    ],
    [
        InlineKeyboardButton(text="💼 Управление", callback_data="management")
    ],
    [
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")
    ]
])
