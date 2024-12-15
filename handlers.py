from aiogram import Router, F, Bot, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, message_id, CallbackQuery, InlineKeyboardButton, \
    InputFile, FSInputFile, InlineKeyboardMarkup, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
# from aiogram.filters.callback_data import CallbackData
# from aiogram.enums import ParseMode
# from pyexpat.errors import messages


from database.db import DataBase
import text
import html
import logging

#версия с карточками
db = DataBase()
router = Router()
# tickets = {}
# admins = [123456789, 987654321]  # ID админов
# ticket_cb = CallbackData("ticket", "action", "ticket_id")  # Для кнопок


class Form(StatesGroup):
    institution = State()
    specialty = State()
    subject = State()
    full_name = State()
    teach_experience = State()
    time_slot = State()
    pay_services = State()
    contact_telegram = State()
    contact = State()
    contact_manual = State()
    #request = State()
    #reject_request = State()
    #accept_request = State()
    #accept_request_student = State()


class Filters(StatesGroup):
    institution = State()
    specialty = State()
    subject = State()
    teach_experience = State()
    time_slot = State()
    pay_services = State()
    search = State()
    one_institution = State()
    one_specialty = State()
    one_subject = State()
    one_teach_experience = State()
    one_time_slot = State()
    one_pay_services = State()
    one_search = State()
    publications_with_filters = State()
    waiting_for_search = State()

print("v1.0")
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
        'Отлично, с выбором определились',
        reply_markup=user_keyboard
    )
    await call.answer()

@router.callback_query(F.data == 'tutor')
async def tutor_handler(call: CallbackQuery):
    kb = [[KeyboardButton(text='Опубликовать анкету')],
          [KeyboardButton(text='Главная')],
          [KeyboardButton(text='Тех. поддержка')]]
    user_keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await call.message.answer(
        'Отлично, с выбором определились',
        reply_markup=user_keyboard
    )
    await call.answer()

# @router.message(F.text == 'Тех. поддержка')
# @router.message(Command(commands=["tech_support"]))
# async def tech_support_handler(message: types.Message):
#     if message.from_user.id in tickets:
#         await message.answer("Вы уже отправили обращение. Дождитесь ответа.")
#         return
#
#     await message.answer("Пожалуйста, напишите ваше обращение.")
#     tickets[message.from_user.id] = {
#         "text": None,
#         "status": "new",
#         "admin_id": None,
#         "transfers_count": 0,
#         "history": [],
#         "username": message.from_user.username,
#     }
#     await message.answer("Пожалуйста, напишите ваше обращение.")
#
# #обработка текста обращения
# @router.message(lambda msg: msg.from_user.id in tickets and tickets[msg.from_user.id]["status"] == "new")
# async def handle_user_message(message: types.Message):
#     ticket = tickets[message.from_user.id]
#     ticket["text"] = message.text
#     ticket["status"] = "in_progress"
#     ticket["admin_id"] = admins[0]
#     ticket["history"].append({"sender": "user", "message": message.text})
#
#     keyboard = InlineKeyboardMarkup().add(
#         InlineKeyboardButton("Ответить", callback_data=ticket_cb.new("reply", message.from_user.id)),
#         InlineKeyboardButton("Передать другому", callback_data=ticket_cb.new("transfer", message.from_user.id)),
#         InlineKeyboardButton("Отклонить", callback_data=ticket_cb.new("reject", message.from_user.id)),
#     )
#
#     await message.answer("Ваше обращение отправлено в поддержку.")
#     await message.bot.send_message(
#         admins[0],
#         f"Новое обращение от {message.from_user.username}:\n\n{message.text}",
#         reply_markup=keyboard,
#     )
#
# #Обработка кнопок админа
# @router.callback_query(ticket_cb.filter(action=["reply", "transfer", "reject"]))
# async def admin_actions(query: CallbackQuery, callback_data: ticket_cb):
#     action = callback_data["action"]
#     user_id = int(callback_data["ticket_id"])
#     ticket = tickets[user_id]
#
#     if action == "reply":
#         ticket["status"] = "waiting_admin_reply"
#         await query.message.answer("Введите ваш ответ.")
#     elif action == "transfer":
#         ticket["transfers_count"] += 1
#         if ticket["transfers_count"] >= len(admins):
#             await query.message.answer("Обращение автоматически отклонено.")
#             ticket["status"] = "rejected"
#             await query.message.bot.send_message(
#                 user_id,
#                 f"Ваше обращение: {ticket['text']}\n\nМы не смогли его обработать. Попробуйте снова позже.",
#             )
#         else:
#             next_admin = admins[ticket["transfers_count"]]
#             ticket["admin_id"] = next_admin
#             keyboard = InlineKeyboardMarkup().add(
#                 InlineKeyboardButton("Ответить", callback_data=ticket_cb.new("reply", user_id)),
#                 InlineKeyboardButton("Передать другому", callback_data=ticket_cb.new("transfer", user_id)),
#                 InlineKeyboardButton("Отклонить", callback_data=ticket_cb.new("reject", user_id)),
#             )
#             await query.message.bot.send_message(
#                 next_admin,
#                 f"Обращение от {ticket['username']} передано вам:\n\n{ticket['text']}",
#                 reply_markup=keyboard,
#             )
#     elif action == "reject":
#         ticket["status"] = "rejected"
#         await query.message.answer("Введите причину отклонения.")



@router.message(F.text == 'Тех. поддержка')
async def tech_support_handler(message: Message, state: FSMContext):
   admin_contact = "@Mihter_2208,\t@fazylov_v,\n@irinacreek,\t@Yazshiopl"  # Замените на реальный юзернейм администратора
   admins = admin_contact.split()
   await state.update_data(admins=admins)

   # Создаем клавиатуру НЕ СТОИТ ЭТО ДЕЛАТЬ
   # keyboard = InlineKeyboardMarkup(inline_keyboard=[
   #     [InlineKeyboardButton(text='Чат с администрацией', callback_data='chat_with_admin')]
   # ])

   # Путь к изображению
   photo_path = './img/TPimage.jpg'

   # Отправка фото с подписью
   await message.answer_photo(photo=FSInputFile(photo_path),  # Передаем путь к файлу
                              caption="Если у вас возникли вопросы или проблемы, вы можете обратиться в техподдержку:\n\n"
                                      f"Контакты администрации: {admin_contact}\n"
                                      f"Мы рады помочь вам!")
   #await message.answer(
   #    f"Если у вас возникли вопросы или проблемы, вы можете обратиться в техподдержку:\n\n"
   #    f"Контакты администрации: {admin_contact}\n"
   #    f"Мы рады помочь вам!")#\nМожете начать \"чат с администрацией\", если контакты выше не доступны.", reply_markup=keyboard)



#поиск репетиторов
# Обработчик для текстового сообщения
@router.message(F.text == 'Поиск репетитора')
async def search_tutors_message_handler(message: Message, state: FSMContext):
    await state.clear()
    # Отправляем сообщение с выбором способа поиска
    await message.answer("Как вы хотите искать репетитора?\nВыберите один из вариантов:",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [InlineKeyboardButton(text="Все публикации", callback_data="all_publications")],
                             [InlineKeyboardButton(text="С фильтрами", callback_data="with_filters")]
                         ]))

#отображение всех публикаций
@router.callback_query(F.data == 'all_publications')
async def all_publications_handler(call: CallbackQuery, state: FSMContext):
    await state.clear()
    # отображение числа всех публикаций
    total_publications = db.get_publications_count()
    if total_publications == 0:
        await call.message.answer("На данный момент нет доступных репетиторов.")
        return

    per_page = 5  # Количество публикаций на странице
    page_count = (total_publications // per_page) + (1 if total_publications % per_page else 0)
    await state.update_data(total_publications=total_publications, total_pages=page_count, current_page=1)
    await display_publications(call.message, state, 1, per_page)


@router.callback_query(F.data == 'with_filters')
async def with_filters_handler(call: CallbackQuery, state: FSMContext):
    # Отправляем сообщение с выбором фильтров
    await call.message.answer("<b>Выберите фильтр.</b>\n<i>Сбрасываются только при повторном нажатии <b>\"Поиск репетитора\"</b> или <b>\"Все публикации\"</b></i>:",
                              reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                  [InlineKeyboardButton(text="Все фильтры", callback_data="all_filters")],
                                  [InlineKeyboardButton(text="Учреждение", callback_data="institution")],
                                  [InlineKeyboardButton(text="Специальность", callback_data="specialty")],
                                  [InlineKeyboardButton(text="Предмет", callback_data="subject")],
                                  [InlineKeyboardButton(text="Опыт преподавателя", callback_data="experience")],
                                  [InlineKeyboardButton(text="Время занятия", callback_data="time_slot")],
                                  [InlineKeyboardButton(text="Стоимость занятия", callback_data="price")]
                              ]))
    await call.answer()


#Фильтры
#все фильтры
@router.callback_query(F.data == 'all_filters')
async def all_filters_handler(call: CallbackQuery, state: FSMContext):
    # Запрашиваем все фильтры по порядку
    await call.message.answer("Введите Учреждение:")
    await state.set_state(Filters.institution)
    print("Состояние установлено на Filters.institution")
    current_state = await state.get_state()
    print(f"Текущее состояние: {current_state}")


#фильтр по учреждению
@router.callback_query(F.data == 'institution')
async def institution_handler(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Введите Учреждение:")
    await state.set_state(Filters.one_institution)


#фильтр по специальности
@router.callback_query(F.data == 'specialty')
async def specialty_handler(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Введите Специальность:")
    await state.set_state(Filters.one_specialty)


#фильтр по предмету
@router.callback_query(F.data == 'subject')
async def specialty_handler(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Введите Предмет:")
    await state.set_state(Filters.one_subject)


#фильтр по опыту преподавания
@router.callback_query(F.data == 'experience')
async def experience_handler(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Введите Опыт преподавания:")
    await state.set_state(Filters.one_teach_experience)


#фильтр по времени занятия
@router.callback_query(F.data == 'time_slot')
async def time_slot_handler(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Введите Время занятия:")
    await state.set_state(Filters.one_time_slot)


#фильтр по стоимости занятия
@router.callback_query(F.data == 'price')
async def price_handler(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Введите максимальную Стоимость занятия:")
    await state.set_state(Filters.one_pay_services)


#запрос института
@router.message(Filters.institution)
async def process_institution(message: Message, state: FSMContext):
    institution = message.text
    print("Обработчик для учреждения сработал")  # Отладочное сообщение
    await state.update_data(institution=institution)
    await message.answer("Учреждение сохранено. Теперь введите Специальность:")
    await state.set_state(Filters.specialty)


# Запрос специальности
@router.message(Filters.specialty)
async def process_specialty(message: Message, state: FSMContext):
    specialty = message.text
    await state.update_data(specialty=specialty)
    await message.answer("Специальность сохранена. Теперь введите Предмет:")
    await state.set_state(Filters.subject)

# Запрос предмета
@router.message(Filters.subject)
async def process_subject(message: Message, state: FSMContext):
    subject = message.text
    await state.update_data(subject=subject)
    await message.answer("Предмет сохранен. Теперь введите Опыт преподавания:")
    await state.set_state(Filters.teach_experience)

# Запрос опыта
@router.message(Filters.teach_experience)
async def process_teach_experience(message: Message, state: FSMContext):
    teach_experience = message.text
    await state.update_data(teach_experience=teach_experience)
    await message.answer("Опыт преподавания сохранен. Теперь введите Время занятия:")
    await state.set_state(Filters.time_slot)

# Запрос времени
@router.message(Filters.time_slot)
async def process_time_slot(message: Message, state: FSMContext):
    time_slot = message.text
    await state.update_data(time_slot=time_slot)
    await message.answer("Время занятия сохранено. Теперь введите Стоимость занятия:")
    await state.set_state(Filters.pay_services)

#запрос стоимости
@router.message(Filters.pay_services)
async def process_pay_services(message: Message, state: FSMContext):
    pay_services = message.text
    await state.update_data(pay_services=pay_services)

    # Получаем все данные, которые были собраны
    data = await state.get_data()
    institution = data.get('institution')
    specialty = data.get('specialty')
    subject = data.get('subject')
    teach_experience = data.get('teach_experience')
    time_slot = data.get('time_slot')
    pay_services = data.get('pay_services')

    await message.answer("Ваши данные успешно собраны:\n"
                         f"Учреждение: {institution}\n"
                         f"Специальность: {specialty}\n"
                         f"Предмет: {subject}\n"
                         f"Опыт преподавания: {teach_experience}\n"
                         f"Время занятия: {time_slot}\n"
                         f"Стоимость занятия: {pay_services}\n"
                         "Теперь мы можем выполнить поиск репетиторов по этим критериям.",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [InlineKeyboardButton(text="Поиск", callback_data="filtered_search")]
                         ]))
    # Установите состояние для ожидания нажатия кнопки "Поиск"
    await state.set_state(Filters.waiting_for_search)
    #await state.set_state(Filters.publications_with_filters)
    #await filtered_publications_handler(message, state)


@router.message(Filters.one_institution)
async def process_institution(message: Message, state: FSMContext):
    await state.update_data(institution=message.text)
    await message.answer("Учреждение получено. Начать поиск?",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [InlineKeyboardButton(text="Поиск", callback_data="filtered_search")]
                         ]))
    await state.set_state(Filters.waiting_for_search)
    #await state.set_state(Filters.publications_with_filters)
    #await filtered_publications_handler(message, state)



@router.message(Filters.one_specialty)
async def process_specialty(message: Message, state: FSMContext):
    await state.update_data(specialty=message.text)
    await message.answer("Специальность сохранена. Начать поиск?",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [InlineKeyboardButton(text="Поиск", callback_data="filtered_search")]
                         ]))
    await state.set_state(Filters.waiting_for_search)
    #await filtered_publications_handler(message, state)
    #await state.set_state(Filters.publications_with_filters)


@router.message(Filters.one_subject)
async def process_subject(message: Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await message.answer("Предмет сохранен. Начать поиск?",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [InlineKeyboardButton(text="Поиск", callback_data="filtered_search")]
                         ]))
    await state.set_state(Filters.waiting_for_search)
    #await filtered_publications_handler(message, state)
    # await state.set_state(Filters.publications_with_filters)


@router.message(Filters.one_teach_experience)
async def process_teach_experience(message: Message, state: FSMContext):
    await state.update_data(teach_experience=message.text)
    await message.answer("Опыт преподавания сохранен. Начать поиск?",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [InlineKeyboardButton(text="Поиск", callback_data="filtered_search")]
                         ]))
    await state.set_state(Filters.waiting_for_search)
    #await filtered_publications_handler(message, state)
    # await state.set_state(Filters.publications_with_filters)


@router.message(Filters.one_time_slot)
async def process_time_slot(message: Message, state: FSMContext):
    await state.update_data(time_slot=message.text)
    await message.answer("Время занятия сохранено. Начать поиск?",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [InlineKeyboardButton(text="Поиск", callback_data="filtered_search")]
                         ]))
    await state.set_state(Filters.waiting_for_search)
    #await filtered_publications_handler(message, state)
    #await state.set_state(Filters.publications_with_filters)


@router.message(Filters.one_pay_services)
async def process_pay_services(message: Message, state: FSMContext):
    await state.update_data(pay_services=message.text)
    await message.answer("Стоимость занятия сохранена. Начать поиск?",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [InlineKeyboardButton(text="Поиск", callback_data="filtered_search")]
                         ]))
    await state.set_state(Filters.waiting_for_search)
    #await filtered_publications_handler(message, state)
    # await state.set_state(Filters.publications_with_filters)

#Поиск
#@router.message(Filters.publications_with_filters)
@router.callback_query(F.data == 'filtered_search')
async def filtered_publications_handler(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Идёт поиск...")
    # отображение числа всех публикаций
    data = await state.get_data()
    institution = data.get('institution')
    specialty = data.get('specialty')
    subject = data.get('subject')
    teach_experience = data.get('teach_experience')
    time_slot = data.get('time_slot')
    pay_services = data.get('pay_services')
    #тута я получаю количество публикаций подходящих под фильтры
    total_publications = db.get_filtered_publications_count(institution, specialty, subject, teach_experience, time_slot, pay_services)
    if total_publications == 0:
        await call.message.answer("На данный момент нет доступных репетиторов.")
        return

    per_page = 5  # Количество публикаций на странице
    page_count = (total_publications // per_page) + (1 if total_publications % per_page else 0)
    await state.update_data(total_publications=total_publications, total_pages=page_count, current_page=1, isFilter=1)
    await display_publications(call.message, state, 1, per_page, institution, specialty, subject, teach_experience, time_slot, pay_services)


# Функция отображения публикаций
async def display_publications(message_or_call: Message, state: FSMContext, page: int, per_page: int, institution=None, specialty=None, subject=None, teach_experience=None, time_slot=None, pay_services=None):
    data = await state.get_data()
    institution = data.get('institution')
    specialty = data.get('specialty')
    subject = data.get('subject')
    teach_experience = data.get('teach_experience')
    time_slot = data.get('time_slot')
    pay_services = data.get('pay_services')
    total_pages = data.get('total_pages', 1)
    total_publications = data.get('total_publications')
    isFilter = data.get('isFilter')
    try:
        get_sent: list[Message] = data.get('sent_messages')
        for m in get_sent:
            await m.delete()

    except:
        pass

    #можно просто так:
    #publications = db.get_publications_for_page_with_filters(page, per_page, institution, specialty, subject, teach_experience, time_slot, pay_services)
    if isFilter != 1:
        publications = db.get_publications_for_page(page, per_page)
    else:
        publications = db.get_publications_for_page_with_filters(page, per_page, institution, specialty, subject, teach_experience, time_slot, pay_services)

    i=(page-1)*per_page
    sent_messages = []
    for pub in publications:
        i+=1
        publication_text = f"<b><i>Публикация:</i></b> {i}\n" \
                           f"<b><i>Репетитор:</i></b> {pub[2]}\n" \
                           f"<b><i>Учреждение:</i></b> {pub[3]}\n" \
                           f"<b><i>Специальность(направление):</i></b> {pub[4]}\n" \
                           f"<b><i>Предмет:</i></b> {pub[5]}\n" \
                           f"<b><i>Опыт преподавания:</i></b> {pub[7]}\n" \
                           f"<b><i>Удобное время:</i></b> {pub[8]}\n" \
                           f"<b><i>Стоимость услуги:</i></b> {pub[9]}\n" \
                           f"<b><i>Контактные данные:</i></b> {pub[6]}"

        sent_message: Message = await message_or_call.answer(publication_text)
        sent_messages.append(sent_message)

    await state.update_data(sent_messages=sent_messages)

        #,
                                     #reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                     #    [InlineKeyboardButton(text="Подать заявку", callback_data=f"apply_for_tutor_{pub[0]}_{pub[1]}")]
                                     #]))
    # Добавление информации о текущей странице и кнопок навигации
    navigation_keyboard = InlineKeyboardBuilder()
    if page > 1:
        navigation_keyboard.add(InlineKeyboardButton(text="Предыдущая", callback_data="prev_page"))
    if page < total_pages:
        navigation_keyboard.add(InlineKeyboardButton(text="Следующая", callback_data="next_page"))

    sent_message = await message_or_call.answer(f"Всего публикаций: {total_publications}\n"f"Страница {page} из {total_pages}", reply_markup=navigation_keyboard.as_markup())
    sent_messages.append(sent_message)
    await state.update_data(sent_messages=sent_messages)
    await state.update_data(current_page=page)

# Обработчики кнопок навигации
@router.callback_query(lambda call: call.data in ['prev_page', 'next_page'])
async def navigate_pages_handler(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_page = data.get('current_page', 1)
    total_pages = data.get('total_pages', 1)
    #isFilter = data.get('isFilter')

    new_page = current_page - 1 if call.data == 'prev_page' else current_page + 1
    if 1 <= new_page <= total_pages:
        await display_publications(call.message, state, new_page, 5 )
    await call.answer()


# @router.callback_query(F.data.startswith("apply_for_tutor"))
# async def apply_for_tutor(call: CallbackQuery,  state: FSMContext):
#
#     # Извлекаем tutor_id из callback_data
#     list_tut_pub = call.data.split('_') # Разделяем по символу "_" и получаем tutor_id
#     tutor_id = list_tut_pub[-1]
#     publication_id = list_tut_pub[-2]
#     await state.update_data(tutor_id=tutor_id, publication_id=publication_id)
#
#     await call.message.answer(text.request_example)
#     await state.set_state(Form.request)
#
# @router.message(Form.request)
# async def send_request(message: Message, state: FSMContext, bot: Bot):
#     request_text = message.text
#     data = await state.get_data()
#     student_id = message.from_user.id
#     tutor_id = data["tutor_id"]
#     publication_id = data["publication_id"]
#     await state.update_data(student_id=student_id)
#
#     db.add_request(student_id, tutor_id, publication_id, request_text)
#
#     builder = InlineKeyboardBuilder()
#     builder.row(
#         InlineKeyboardButton(text="Принять", callback_data=f"accept_request_{student_id}_{publication_id}"),
#         InlineKeyboardButton(text="Отклонить", callback_data=f"reject_request_{student_id}_{publication_id}")
#     )
#
#     await bot.send_message(
#         chat_id=tutor_id,
#         text=f"На вашу заявку откликнулись:\n"
#              f"Текст заявки: {request_text}\n\n"
#              f"Принять или отклонить заявку?",
#         reply_markup=builder.as_markup()
#     )
#
#     await message.answer('Заявка успешно отправлена!\nКогда преподаватель ответит, вам придет сообщение, пока можете оставить другие заявки. ')
#
#
# @router.callback_query(F.data.startswith("accept_request"))
# async def accept_request(call: CallbackQuery, state: FSMContext):
#     list_accept_request = call.data.split('_')
#     student_id = list_accept_request[-2]
#     publication_id = list_accept_request[-1]
#     await state.update_data(student_id=student_id, publication_id=publication_id)
#
#     await call.message.answer("Пожалуйста, введите обратную связь по запросу студента:")
#     await state.set_state(Form.accept_request)
#
#
# @router.message(Form.accept_request)
# async def process_feedback(message: Message, state: FSMContext):
#     feedback = message.text
#     await state.update_data(feedback=feedback)
#
#     await message.answer("Теперь введите стоимость ваших услуг (например, '1000 рублей'):")
#     await state.set_state(Form.accept_request_student)  # Переходим в тот же статус, чтобы получать следующую информацию
#
#
# @router.message(Form.accept_request_student)
# async def process_price(message: Message, state: FSMContext, bot: Bot):
#     price = message.text
#     data = await state.get_data()
#     student_id = data["student_id"]
#     feedback = data["feedback"]
#     tutor_username = message.from_user.username
#     await state.update_data(tutor_username=tutor_username)
#
#     pay_keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[
#             #можно вставить url=ссылка на оплату
#             [InlineKeyboardButton(text="Оплатить", callback_data=f"handle_payment_{tutor_username}_{student_id}")]
#         ]
#     )
#     # Отправляем студенту обратную связь и цену
#     await bot.send_message(
#         chat_id=student_id,
#         text=f"Репетитор дал(а) вам обратную связь:\n\n{feedback}\n\nСтоимость услуг: {price}\n\nДля продолжения нажмите кнопку ниже.",
#         reply_markup=pay_keyboard
#     )
#
#     await message.answer("Обратная связь и стоимость успешно отправлены студенту.")
#     #await state.clear()  # Очистка состояния после завершения процесса
#
#
# #@router.message(Form.accept_request_student)
# @router.callback_query(F.data.startswith("handle_payment"))
# async def handle_payment(call: CallbackQuery, state: FSMContext, bot: Bot):
#     student_id = F.data.split('_')[-1]# Юзернейм репетитора из состояния
#     tutor_username = F.data.split('_')[-2]
#
#     # Отправляем сообщение студенту, что оплата пока не поступила
#     await bot.send_message(
#         chat_id=student_id,
#         text="Оплаты пока нет. Вот чат с репетитором: @"+tutor_username
#     )
#     await call.answer()
#     await state.clear()  # Очистка состояния после завершения процесса
#
#
# @router.callback_query(F.data.startswith("reject_request"))
# async def reject_request(call: CallbackQuery, state: FSMContext):
#     list_reject_request = call.data.split('_')
#     student_id = list_reject_request[-2]
#     publication_id = list_reject_request[-1]
#     await state.update_data(student_id=student_id, publication_id=publication_id)
#
#     await call.message.answer("Пожалуйста, введите причину отказа:")
#     await state.set_state(Form.reject_request)
#
#
# @router.message(Form.reject_request)
# async def process_reject_reason(message: Message, state: FSMContext, bot: Bot):
#     reject_reason = message.text
#     data = await state.get_data()
#     student_id = data["student_id"]
#
#     # Отправка сообщения студенту
#     await bot.send_message(
#         chat_id=student_id,
#         text=f"Ваша заявка была отклонена.\nПричина: {reject_reason}"
#     )
#
#     await message.answer("Причина отказа успешно отправлена студенту.")
#     await state.clear()


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
    await message.answer("ФИО (как к вам обращаться):")
    await state.set_state(Form.full_name)

#получаем фулл нейм и просим учреждение
@router.message(Form.full_name)
async def process_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("Введите учреждение:")
    await state.set_state(Form.institution)

#получаем учреждение и просим специальность
@router.message(Form.institution)
async def process_institution(message: Message, state: FSMContext):
    await state.update_data(institution=message.text)
    await message.answer("Введите специальность:")
    await state.set_state(Form.specialty)

#получаем специальность и просим предмет
@router.message(Form.specialty)
async def process_specialty(message: Message, state: FSMContext):
    await state.update_data(specialty=message.text)
    await message.answer("Введите предмет:")
    await state.set_state(Form.subject)

#получаем предмет и просит опыт преподавания
@router.message(Form.subject)
async def process_subject(message: Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await message.answer("Введите ваш опыт преподавания (в годах):")
    await state.set_state(Form.teach_experience)

#получаем опыт преподавания и просим ввести время для занятий
@router.message(Form.teach_experience)
async def process_teach_experience(message: Message, state: FSMContext):
    await state.update_data(teach_experience=message.text)
    await message.answer("Введите время, когда удобно проводить занятия (или по договорённости):")
    await state.set_state(Form.time_slot)

# получаем опыт преподавания и просит цену услуг
@router.message(Form.time_slot)
async def process_time_slot(message: Message, state: FSMContext):
    await state.update_data(time_slot=message.text)
    await message.answer("Введите стоимость услуг, например, 1500 рублей (или по договорённости):")
    await state.set_state(Form.pay_services)


# получаем цену услуг и просит контакты
@router.message(Form.pay_services)
async def process_pay_services(message: Message, state: FSMContext):
    await state.update_data(pay_services=message.text)

    # создаем клавиатуру
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Телеграмм", callback_data="contact_telegram"),
        InlineKeyboardButton(text="Ввести вручную", callback_data="contact_manual")
    )

    await message.answer("Как с вами связаться?", reply_markup=builder.as_markup())


# Обработчик для кнопки "Телеграмм"
@router.callback_query(lambda c: c.data == "contact_telegram")
async def process_contact_telegram(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    full_name = data.get('full_name')
    if (full_name == None):
        await callback_query.message.answer(
            "Анкета уже отправлена, для заполнения новой нажмите \"Опубликовать анкету\"")
        return

    await callback_query.message.answer("Получаем данные...")

    # Получаем информацию о пользователе
    user = callback_query.from_user
    username = "@" + user.username
    tutor_id = user.id

    if username:
        await state.update_data(contact=username)
        await state.update_data(tutor_id=tutor_id)
        await finalize_publication(callback_query.message, state)
    else:
        # Если юзернейм отсутствует, просим ввести контакт вручную
        await callback_query.message.answer("У вас не указан юзернейм. Пожалуйста, введите ваш контакт вручную:")
        await state.set_state(Form.contact_manual)


@router.message(Form.contact_telegram)
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


# Обработчик для кнопки "Ввести вручную"
@router.callback_query(lambda c: c.data == "contact_manual")
async def process_contact_manual(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    full_name = data.get('full_name')
    if (full_name == None):
        await callback_query.message.answer(
            "Анкета уже отправлена, для заполнения новой нажмите \"Опубликовать анкету\"")
        return
    await callback_query.message.answer("Пожалуйста, введите ваш контакт:")

    # Устанавливаем состояние для ввода контакта
    await state.set_state(Form.contact_manual)


@router.message(Form.contact_manual)
async def process_manual_contact(message: Message, state: FSMContext):
    contact = message.text
    await state.update_data(contact=contact)
    tutor_id = message.from_user.id
    await state.update_data(tutor_id=tutor_id)
    await message.answer(f"Контактные данные сохранены: {contact}")
    await finalize_publication(message, state)

#Финал с отправкой формы анкеты
async def finalize_publication(message: Message, state: FSMContext):
    # Получаем все данные
    data = await state.get_data()
    full_name = data.get('full_name')
    institution = data.get('institution')
    specialty = data.get('specialty')
    subject = data.get('subject')
    teach_experience = data.get('teach_experience')
    time_slot = data.get('time_slot')
    pay_services = data.get('pay_services')
    contact = data.get('contact')
    tutor_id = data.get('tutor_id')

    # Здесь вы можете добавить код для сохранения данных в БД
    db.add_publication(tutor_id, full_name, institution, specialty, subject, teach_experience, time_slot, pay_services, contact)

    # Формируем сообщение
    message_text = (
            "Ваша публикация успешно размещена:\n" +
            f"{full_name} разместил(а) объявление о репетиторстве.\n" +
            f"Учреждение: {institution}\n" +
            f"Специальность(направление): {specialty}\n" +
            f"Предмет: {subject}\n" +
            f"Опыт преподавания: {teach_experience}\n" +
            f"Удобное время: {time_slot}\n" +
            f"Стоимость услуги: {pay_services}\n" +
            f"Контактные данные: {contact}"
    )
    logging.info(f"Длина сообщения: {len(message_text)}")
    # Проверяем длину сообщения и разбиваем, если необходимо
    max_length = 4096
    if len(message_text) > max_length:
        # Разбиваем сообщение на части
        for i in range(0, len(message_text), max_length):
            await message.answer(message_text[i:i + max_length])
    else:
        await message.answer(message_text)

    await state.clear()



