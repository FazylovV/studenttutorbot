from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, message_id, CallbackQuery, InlineKeyboardButton, \
    InputFile, FSInputFile, InlineKeyboardMarkup, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pyexpat.errors import messages

from database.db import DataBase
import text
import html


db = DataBase()
router = Router()

class Form(StatesGroup):
    institution = State()
    specialty = State()
    subject = State()
    full_name = State()
    contact = State()
    contact_manual = State()
    request = State()
    reject_request = State()
    accept_request = State()
    accept_request_student = State()

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

    publications_text = "\n\n".join([f"<i>Публикация {i+1}</i>: {pub[2]}, {pub[3]}, {pub[4]}, <b>{pub[5]}</b>, {pub[6]}" for i, pub in enumerate(publications)])

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="<<", callback_data="prev_page"),
        InlineKeyboardButton(text=f"1/{page_count}", callback_data="current_page"),
        InlineKeyboardButton(text=">>", callback_data="next_page")
    )
    #добавление кнопки с tutor_id в callback_data
    i = 1
    for pub in publications:
        builder.row(
            InlineKeyboardButton(text=f"Подать заявку на {i} публикацию", callback_data=f"apply_for_tutor_{pub[0]}_{pub[1]}")
        )
        i += 1

    await call.answer(
        f"Всего публикаций: {total_publications}\n\n{publications_text}",
        reply_markup=builder.as_markup()
    )
    #await call.answer()

@router.callback_query(F.data.startswith("apply_for_tutor"))
async def apply_for_tutor(call: CallbackQuery,  state: FSMContext):

    # Извлекаем tutor_id из callback_data
    list_tut_pub = call.data.split('_') # Разделяем по символу "_" и получаем tutor_id
    tutor_id = list_tut_pub[-1]
    publication_id = list_tut_pub[-2]
    await state.update_data(tutor_id=tutor_id, publication_id=publication_id)

    await call.message.answer(text.request_example)
    await state.set_state(Form.request)

@router.message(Form.request)
async def send_request(message: Message, state: FSMContext, bot: Bot):
    request_text = message.text
    data = await state.get_data()
    student_id = message.from_user.id
    tutor_id = data["tutor_id"]
    publication_id = data["publication_id"]
    await state.update_data(student_id=student_id)

    db.add_request(student_id, tutor_id, publication_id, request_text)

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Принять", callback_data=f"accept_request_{student_id}_{publication_id}"),
        InlineKeyboardButton(text="Отклонить", callback_data=f"reject_request_{student_id}_{publication_id}")
    )

    await bot.send_message(
        chat_id=tutor_id,
        text=f"На вашу заявку откликнулись:\n"
             f"Текст заявки: {request_text}\n\n"
             f"Принять или отклонить заявку?",
        reply_markup=builder.as_markup()
    )

    await message.answer('Заявка успешно отправлена!\nКогда преподаватель ответит, вам придет сообщение, пока можете оставить другие заявки. ')


@router.callback_query(F.data.startswith("accept_request"))
async def accept_request(call: CallbackQuery, state: FSMContext):
    list_accept_request = call.data.split('_')
    student_id = list_accept_request[-2]
    publication_id = list_accept_request[-1]
    await state.update_data(student_id=student_id, publication_id=publication_id)

    await call.message.answer("Пожалуйста, введите обратную связь по запросу студента:")
    await state.set_state(Form.accept_request)


@router.message(Form.accept_request)
async def process_feedback(message: Message, state: FSMContext):
    feedback = message.text
    await state.update_data(feedback=feedback)

    await message.answer("Теперь введите стоимость ваших услуг (например, '1000 рублей'):")
    await state.set_state(Form.accept_request_student)  # Переходим в тот же статус, чтобы получать следующую информацию


@router.message(Form.accept_request_student)
async def process_price(message: Message, state: FSMContext, bot: Bot):
    price = message.text
    data = await state.get_data()
    student_id = data["student_id"]
    feedback = data["feedback"]
    tutor_username = message.from_user.username
    await state.update_data(tutor_username=tutor_username)

    pay_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            #можно вставить url=ссылка на оплату
            [InlineKeyboardButton(text="Оплатить", url=f"https://t.me/{tutor_username}", callback_data=f"handle_payment_{tutor_username}_{student_id}")]
        ]
    )
    # Отправляем студенту обратную связь и цену
    await bot.send_message(
        chat_id=student_id,
        text=f"Репетитор дал(а) вам обратную связь:\n\n{feedback}\n\nСтоимость услуг: {price}\n\nДля продолжения нажмите кнопку ниже.",
        reply_markup=pay_keyboard
    )

    await message.answer("Обратная связь и стоимость успешно отправлены студенту.")
    #await state.clear()  # Очистка состояния после завершения процесса


#@router.message(Form.accept_request_student)
@router.callback_query(F.data.startswith("handle_payment"))
async def handle_payment(call: CallbackQuery, state: FSMContext, bot: Bot):
    student_id = F.data.split('_')[-1]# Юзернейм репетитора из состояния
    tutor_username = F.data.split('_')[-2]

    # Отправляем сообщение студенту, что оплата пока не поступила
    await bot.send_message(
        chat_id=student_id,
        text="Оплаты пока нет. Вот чат с репетитором: @"+tutor_username
    )
    await call.answer()
    await state.clear()  # Очистка состояния после завершения процесса


@router.callback_query(F.data.startswith("reject_request"))
async def reject_request(call: CallbackQuery, state: FSMContext):
    list_reject_request = call.data.split('_')
    student_id = list_reject_request[-2]
    publication_id = list_reject_request[-1]
    await state.update_data(student_id=student_id, publication_id=publication_id)

    await call.message.answer("Пожалуйста, введите причину отказа:")
    await state.set_state(Form.reject_request)


@router.message(Form.reject_request)
async def process_reject_reason(message: Message, state: FSMContext, bot: Bot):
    reject_reason = message.text
    data = await state.get_data()
    student_id = data["student_id"]

    # Отправка сообщения студенту
    await bot.send_message(
        chat_id=student_id,
        text=f"Ваша заявка была отклонена.\nПричина: {reject_reason}"
    )

    await message.answer("Причина отказа успешно отправлена студенту.")
    await state.clear()


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

        publications_text = "\n\n".join([f"<i>Публикация {i+1}</i>: {pub[2]}, {pub[3]}, {pub[4]}, <b>{pub[5]}</b>, {pub[6]}" for i, pub in enumerate(publications)])

        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="<<", callback_data="prev_page"),
            InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data="current_page"),
            InlineKeyboardButton(text=">>", callback_data="next_page")
        )

        # Добавляем кнопку для каждой публикации
        i = 1
        for pub in publications:
            builder.row(
                InlineKeyboardButton(text=f"Подать заявку на {i} публикацию", callback_data=f"apply_for_tutor_{pub[0]}_{pub[1]}")
            )
            i += 1

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

        publications_text = "\n\n".join([f"<i>Публикация {i+1}</i>: {pub[2]}, {pub[3]}, {pub[4]}, <b>{pub[5]}</b>, {pub[6]}" for i, pub in enumerate(publications)])

        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="<<", callback_data="prev_page"),
            InlineKeyboardButton(text=f"{current_page}/{data['total_pages']}", callback_data="current_page"),
            InlineKeyboardButton(text=">>", callback_data="next_page")
        )

        # Добавляем кнопку для каждой публикации
        i = 1
        for pub in publications:
            builder.row(
                InlineKeyboardButton(text=f"Подать заявку на {i} публикацию", callback_data=f"apply_for_tutor_{pub[0]}_{pub[1]}")
            )
            i += 1

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
    #await call.answer()

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



