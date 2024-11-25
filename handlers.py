from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, message_id, CallbackQuery, InlineKeyboardButton, \
    InputFile, FSInputFile, InlineKeyboardMarkup, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
import text

router = Router()

class Form(StatesGroup):
    publication = State()

@router.message(Command("start"))
async def start_handler(message: Message):
    print("Start command received")
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Студент",
        callback_data=f"student"))
    builder.row(InlineKeyboardButton(
        text="Репетитор",
        callback_data="tutor"))
    await message.answer(
        text.hello_text,
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data == 'student')
async def student_handler(call: CallbackQuery):
    kb = [[KeyboardButton(text='Поиск репетитора')],
          [KeyboardButton(text='Главная')],
          [KeyboardButton(text='Тех. поддержка')]]
    user_keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await call.message.answer(
        'Отлично с выбором определились',
        reply_markup=user_keyboard
    )

@router.callback_query(F.data == 'tutor')
async def tutor_handler(call: CallbackQuery):
    kb = [[KeyboardButton(text='Опубликовать анкету')],
          [KeyboardButton(text='Главная')],
          [KeyboardButton(text='Тех. Поддержка')]]
    user_keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await call.message.answer(
        'Отлично, с выбором определились',
        reply_markup=user_keyboard
    )

@router.message(F.text == 'Опубликовать анкету')
async def publication_handler(message: Message, state: FSMContext):
    print('Form started')