from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def get_location_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📍 Локацияни yuborish / Отправить локацию",
                    request_location=True,
                )
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return keyboard


def get_tuman_keyboard():
    tumans = [
        "Bektemir tumani",
        "Chilonzor tumani",
        "Mirobod tumani",
        "Mirzo Ulug‘bek tumani",
        "Olmazor tumani",
        "Sergeli tumani",
        "Shayxontohur tumani",
        "Uchtepa tumani",
        "Yakkasaroy tumani",
        "Yangihayot tumani",
        "Yashnobod tumani",
        "Yunusobod tumani",
    ]

    inline_keyboard = []
    for i in range(0, len(tumans), 2):
        row = [InlineKeyboardButton(text=tumans[i], callback_data=f"tuman_{tumans[i]}")]
        if i + 1 < len(tumans):
            row.append(
                InlineKeyboardButton(
                    text=tumans[i + 1], callback_data=f"tuman_{tumans[i+1]}"
                )
            )
        inline_keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
