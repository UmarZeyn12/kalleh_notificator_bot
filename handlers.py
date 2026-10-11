import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

from states import OrderStates
from keyboards import get_location_keyboard, get_tuman_keyboard

load_dotenv()
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

router = Router()

WELCOME_TEXT = (
    "Assalomu alaykum! 😊\n\n"
    "Buyurtmani rasmiylashtirish uchun, iltimos, quyidagilarni to'g'ri ketma-ketlikda yuboring:\n"
    "1) 📍 Yetkazib berish manzili yoki lokatsiya\n"
    "2) 'Oltin Kuz' setidan nechta kerakligi\n"
    "3) Yashaydigan tumaningiz (rayon)\n"
    "4) Yetkazib berish uchun qulay vaqt\n"
    "5) 📞 Bog'lanish uchun ishlaydigan telefon raqamingiz\n\n"
    "—\n\n"
    "Здравствуйте! 😊\n\n"
    "Для оформления заказа пришлите, пожалуйста, в правильном порядке:\n"
    "1) 📍 Адрес доставки или геолокацию\n"
    "2) Количество сетов 'Oltin Kuz'\n"
    "3) Ваш район (туман)\n"
    "4) Удобное время для доставки\n"
    "5) 📞 Рабочий номер телефона для связи"
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(OrderStates.waiting_for_address)
    await message.answer(WELCOME_TEXT, reply_markup=get_location_keyboard())


@router.message(OrderStates.waiting_for_address)
async def process_address(message: Message, state: FSMContext):
    if message.location:
        lat = message.location.latitude
        lon = message.location.longitude

        yandex_link = f"https://yandex.com/maps/?pt={lon},{lat}&z=17&l=map"
        address_info = yandex_link

        await state.update_data(address=address_info)
    elif message.text:
        await state.update_data(address=message.text)
    else:
        await message.answer(
            "Iltimos, manzilni matn ko'rinishida yuboring yoki lokatsiyadagi tugmani bosing.\nПожалуйста, отправьте адрес текстом или используйте кнопку локации."
        )
        return

    await state.set_state(OrderStates.waiting_for_quantity)
    await message.answer(
        "Rahmat! 'Oltin Kuz' setidan nechta kerak? (Iltimos, raqam bilan yuboring)\n\n"
        "Спасибо! Сколько сетов 'Oltin Kuz' вам нужно? (Пожалуйста, отправьте цифрой)",
        reply_markup=None,
    )


@router.message(OrderStates.waiting_for_quantity)
async def process_quantity(message: Message, state: FSMContext):
    if not message.text:
        await message.answer(
            "Iltimos, miqdorni raqam bilan yuboring.\nПожалуйста, отправьте количество цифрой."
        )
        return

    await state.update_data(quantity=message.text)

    await state.set_state(OrderStates.waiting_for_tuman)
    await message.answer(
        "Iltimos, quyidagi ro'yxatdan o'zingiz yashaydigan tumanni tanlang:\n\n"
        "Пожалуйста, выберите ваш район из списка ниже:",
        reply_markup=get_tuman_keyboard(),
    )


@router.callback_query(OrderStates.waiting_for_tuman, F.data.startswith("tuman_"))
async def process_tuman(callback: CallbackQuery, state: FSMContext):
    tuman_name = callback.data.replace("tuman_", "")
    await state.update_data(tuman=tuman_name)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()

    await state.set_state(OrderStates.waiting_for_time)
    await callback.message.answer(
        f"Tanlangan tuman: <b>{tuman_name}</b> ✅\n\n"
        "Endi buyurtma yetkazib berishi uchun qulay vaqtni yozing (masalan: <i>10:00 - 13:00</i> yoki <i>19:00 dan keyin</i>):\n\n"
        "Теперь напишите удобное время для доставки (например: <i>10:00 - 13:00</i> или <i>после 19:00</i>):",
        parse_mode="HTML",
    )


@router.message(OrderStates.waiting_for_time)
async def process_time(message: Message, state: FSMContext):
    if not message.text:
        await message.answer(
            "Iltimos, vaqtni matn ko'rinishida yuboring.\nПожалуйста, укажите время текстом."
        )
        return

    await state.update_data(delivery_time=message.text)

    await state.set_state(OrderStates.waiting_for_phone)
    await message.answer(
        "Zo'r! Oxirgi qadam: operatorlar siz bilan bog'lanishi uchun <b>haqiqiy ishlaydigan telefon raqamingizni</b> yuboring:\n\n"
        "Отлично! Последний шаг: отправьте <b>реальный рабочий номер телефона</b>, по которому с вами смогут связаться операторы:",
        parse_mode="HTML",
        reply_markup=None,
    )


@router.message(OrderStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    if not message.text:
        await message.answer(
            "Iltimos, telefon raqamingizni matn ko'rinishida yuboring.\nПожалуйста, отправьте номер телефона текстом."
        )
        return

    phone = message.text

    data = await state.get_data()
    address = data.get("address")
    quantity = data.get("quantity")
    tuman = data.get("tuman")
    delivery_time = data.get("delivery_time")

    user = message.from_user
    username_str = f"@{user.username}" if user.username else "Йўқ / Отсутствует"
    user_link = f"<a href='tg://user?id={user.id}'>{user.full_name}</a>"

    admin_message = (
        "🔥 <b>Yangi buyurtma! / Новый заказ!</b>\n\n"
        f"👤 <b>Mijoz / Клиент:</b> {user_link}\n"
        f"🔗 <b>Username:</b> {username_str}\n"
        f"📍 <b>Manzil / Адрес:</b> {address}\n"
        f"📦 <b>Soni / Количество ('Oltin Kuz'):</b> {quantity}\n"
        f"🏙 <b>Tuman / Район:</b> {tuman}\n"
        f"⏰ <b>Vaqt / Время:</b> {delivery_time}\n"
        f"📞 <b>Ishchi telefon / Рабочий телефон:</b> <code>{phone}</code>"
    )

    if ADMIN_CHAT_ID:
        try:
            await message.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=admin_message,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
        except Exception as e:
            print(f"Xatolik adminiga yuborishda: {e}")

    await message.answer(
        "✅ Buyurtmangiz qabul qilindi! Tez orada operatorlarimiz siz bilan bog'lanishadi va buyurtma 1 kun davomida yetkazib beriladi.\n\n"
        "✅ Ваш заказ принят! В ближайшее время с вами свяжутся операторы и заказ будет доставлен течение 1 дня.",
        reply_markup=None,
    )

    await state.clear()
