from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, message_id, CallbackQuery, InlineKeyboardButton, \
    InputFile, FSInputFile, InlineKeyboardMarkup, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pyexpat.errors import messages

from database.db import DataBase
import text


db = DataBase()
router = Router()

class Form(StatesGroup):
    institution = State()
    specialty = State()
    subject = State()
    full_name = State()
    contact = State()
    contact_manual = State()

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
    tg_id = call.from_user.id
    first_name = call.from_user.first_name
    last_name = call.from_user.last_name
    fullname = first_name + (f" {last_name}" if last_name else "")  # Объединяем имя и фамилию
    contact = '@' + call.from_user.username
    db.add_student(tg_id, fullname, contact)
    kb = [[KeyboardButton(text='Поиск репетитора', callback_data="search_tutors")],
          [KeyboardButton(text='Главная')],
          [KeyboardButton(text='Тех. поддержка')]]
    user_keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await call.message.answer(
        'Отлично с выбором определились',
        reply_markup=user_keyboard
    )
    await call.answer()

#поиск репетиторов
@router.message(F.text == 'Поиск репетитора')
@router.callback_query(F.data == 'search_tutors')
async def search_tutors_handler(call: CallbackQuery, state: FSMContext):
    # Получаем общее количество публикаций
    total_publications = db.get_publications_count()

    # Если публикаций нет
    if total_publications == 0:
        await call.message.answer("На данный момент нет доступных репетиторов.")
        await call.answer()
        return

    # Показываем общее количество публикаций и предлагаем перейти на страницу
    page_count = (total_publications // 10) + (1 if total_publications % 10 else 0)

    # Сохраняем количество страниц в состоянии
    await state.update_data(total_pages=page_count, current_page=1)

    # Выводим первую страницу публикаций
    publications = db.get_publications_for_page(1)

    publications_text = "\n\n".join([f"<i>Публикация {i+1}</i>: {pub[2]}, {pub[3]}, <b>{pub[4]}</b>" for i, pub in enumerate(publications)])

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="<<", callback_data="prev_page"),
        InlineKeyboardButton(text=f"1/{page_count}", callback_data="current_page"),
        InlineKeyboardButton(text=">>", callback_data="next_page")
    )
    #добавление кнопки с tutor_id в callback_data
    for pub in publications:
        builder.row(
            InlineKeyboardButton(text="Подать заявку", callback_data=f"apply_for_tutor_{pub[1]}")
        )

    await call.answer(
        f"Всего публикаций: {total_publications}\n\n{publications_text}",
        reply_markup=builder.as_markup()
    )
    #await call.answer()

@router.callback_query(F.data.startswith("apply_for_tutor"))
async def apply_for_tutor(call: CallbackQuery, state: FSMContext):
    student_id = call.from_user.id

    # Извлекаем tutor_id из callback_data
    tutor_id = call.data.split("_")[-1]  # Разделяем по символу "_" и получаем tutor_id

    # Сохраняем заявку на репетитора
    #db.add_request(student_id, tutor_id)
    print(f"Заявка подаётся  репетитор {tutor_id} студент {student_id}")

    await call.answer("Ваша заявка на репетитора подана!")
    #await call.answer()


@router.callback_query(F.data == "next_page")
async def next_page(call: CallbackQuery, state: FSMContext):
    # Получаем текущую страницу из состояния
    data = await state.get_data()
    current_page = data.get("current_page", 1)
    total_pages = data.get("total_pages", 1)

    if current_page < total_pages:
        current_page += 1

        # Сохраняем новую страницу в состояние
        await state.update_data(current_page=current_page)

        # Получаем публикации для текущей страницы
        publications = db.get_publications_for_page(current_page)

        publications_text = "\n\n".join([f"<i>Публикация {i+1}</i>: {pub[2]}, {pub[3]}, <b>{pub[4]}</b>" for i, pub in enumerate(publications)])

        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="<<", callback_data="prev_page"),
            InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data="current_page"),
            InlineKeyboardButton(text=">>", callback_data="next_page")
        )

        # Добавляем кнопку для каждой публикации
        for pub in publications:
            builder.row(
                InlineKeyboardButton(text=f"Подать заявку на {pub[1]}", callback_data=f"apply_for_tutor_{pub[1]}")
            )

        await call.message.edit_text(
            f"Страница {current_page} из {total_pages}\n\n{publications_text}",
            reply_markup=builder.as_markup()
        )

    await call.answer()

@router.callback_query(F.data == "prev_page")
async def prev_page(call: CallbackQuery, state: FSMContext):
    # Получаем текущую страницу из состояния
    data = await state.get_data()
    current_page = data.get("current_page", 1)

    if current_page > 1:
        current_page -= 1

        # Сохраняем новую страницу в состояние
        await state.update_data(current_page=current_page)

        # Получаем публикации для текущей страницы
        publications = db.get_publications_for_page(current_page)

        publications_text = "\n\n".join([f"<i>Публикация {i+1}</i>: {pub[2]}, {pub[3]}, <b>{pub[4]}</b>" for i, pub in enumerate(publications)])

        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="<<", callback_data="prev_page"),
            InlineKeyboardButton(text=f"{current_page}/{data['total_pages']}", callback_data="current_page"),
            InlineKeyboardButton(text=">>", callback_data="next_page")
        )

        # Добавляем кнопку для каждой публикации
        for pub in publications:
            builder.row(
                InlineKeyboardButton(text=f"Подать заявку на {pub[1]}", callback_data=f"apply_for_tutor_{pub[1]}")
            )

        await call.message.edit_text(
            f"Страница {current_page} из {data['total_pages']}\n\n{publications_text}",
            reply_markup=builder.as_markup()
        )

    await call.answer()


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
    await call.answer()

# Возвращаем пользователя к выбору "Студент" или "Репетитор"
@router.message(F.text == 'Главная')
async def main_handler(message: Message):
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

@router.message(F.text == 'Опубликовать анкету')
async def publication_handler(message: Message, state: FSMContext):
    await message.answer("Введите учреждение:")
    await state.set_state(Form.institution)

@router.message(Form.institution)
async def process_institution(message: Message, state: FSMContext):
    await state.update_data(institution=message.text)
    await message.answer("Введите специальность:")
    await state.set_state(Form.specialty)

@router.message(Form.specialty)
async def process_specialty(message: Message, state: FSMContext):
    await state.update_data(specialty=message.text)
    await message.answer("Введите предмет:")
    await state.set_state(Form.subject)

@router.message(Form.subject)
async def process_subject(message: Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await message.answer("ФИО (или просто Кто вы?):")
    await state.set_state(Form.full_name)

@router.message(Form.full_name)
async def process_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("Получаю ваш юзернейм...")
    await process_contact(message, state)

#либо получаем юзернейм, либо просим ввести
@router.message(Form.contact)
async def process_contact(message: Message, state: FSMContext):
    username = message.from_user.username
    tutor_id = message.from_user.id
    if username:
        await state.update_data(contact=username)
        await state.update_data(tutor_id=tutor_id)
        await message.answer("Ваш юзернейм успешно получен!")
    else:
        await message.answer("У вас нет установленного юзернейма. Пожалуйста, введите его вручную:")
        await state.set_state(Form.contact_manual) # просим ввести руками
        return

    await finalize_publication(message, state)

@router.message(Form.contact_manual)
async def process_contact_manual(message: Message, state: FSMContext):
    await state.update_data(contact=message.text)
    await message.answer("Ваш юзернейм успешно получен!")
    await finalize_publication(message, state)

async def finalize_publication(message: Message, state: FSMContext):
    # Получаем все данные
    data = await state.get_data()
    institution = data.get('institution')
    specialty = data.get('specialty')
    subject = data.get('subject')
    full_name = data.get('full_name')
    contact = data.get('contact')
    tutor_id = data.get('tutor_id')

    # Здесь вы можете добавить код для сохранения данных в БД
    db.add_publication(tutor_id, full_name, institution, specialty, subject, contact)

    await message.answer(
        "Ваша публикация успешно размещена:\n" +
        f"{full_name} разместил(а) объявление о репетиторстве.\n" +
        f"Учреждение: {institution}\n" +
        f"Специальность(направление): {specialty}\n" +
        f"Предмет: {subject}\n" +
        f"Контактные данные: @{contact}"
    )

    await state.clear()



