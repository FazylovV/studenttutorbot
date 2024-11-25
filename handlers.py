from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, message_id, CallbackQuery, InlineKeyboardButton, \
    InputFile, FSInputFile, InlineKeyboardMarkup, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder


router = Router()


@router.message(Command("start"))
async def start_handler(message: Message, start=True):
    print("Start command received")
    user_id = message.from_user.id
    username = message.from_user.username
    kb = [[KeyboardButton(text='История'),
           KeyboardButton(text='Избранное')]]
    user_keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(
        'Здарова нахуй ' + username,
        reply_markup=user_keyboard
    )