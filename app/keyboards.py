

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton , InlineKeyboardMarkup, InlineKeyboardButton

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Skin Price Search"), KeyboardButton(text="View Inventory")], 
    [KeyboardButton(text="Steam Profile Search")],
    [KeyboardButton(text="Server Stats")],
    [KeyboardButton(text="CS Price"), KeyboardButton(text="Steam Profile")],
    [KeyboardButton(text="Bot Info")]
    ],
    resize_keyboard=True
)

steam = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Steam Profile", url="https://steamcommunity.com/profiles/123456789")],
    [InlineKeyboardButton(text="Back", callback_data="back_to_main")]
])