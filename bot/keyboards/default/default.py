from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Кнопка1")
        ],
        [
            KeyboardButton(text="Кнопка2")
        ],
        [
            KeyboardButton(text="Кнопка3")
        ]
    ],
    resize_keyboard=True
)