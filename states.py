from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    waiting_for_address = State()
    waiting_for_quantity = State()
    waiting_for_tuman = State()
    waiting_for_time = State()
    waiting_for_phone = State()
