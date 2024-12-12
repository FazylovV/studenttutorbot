import os

import psycopg2 as ps

from database.config import host, user, password, db_name, schema_name


class DataBase:
    def __init__(self):
        self.connection = ps.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
            )
        self.connection.autocommit = True

    # Выполнение SQL-запроса
    def exec_update_query(self, query):

        with self.connection.cursor() as cursor:
            # Выполняем SQL-запрос
            cursor.execute(query)

        # Выполнение SQL-запроса с возвратом данных (для SELECT)

    def exec_query(self, query):
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    # Добавление нового публикации с проверкой наличия tutor_id в tutors
    def add_publication(self, tutor_id, fullname, institution, specialty, subject, teach_experience, time_slot, pay_services, contact):
        # Проверка, существует ли tutor_id в таблице tutors
        existing_tutor = self.exec_query(f"""
            SELECT COUNT(*) FROM {schema_name}.tutors WHERE tg_id = {tutor_id}
        """)

        # Если tutor_id не найден, добавляем нового пользователя
        if existing_tutor[0][0] == 0:
            self.add_tutor(tutor_id, fullname)

        #contact = '@' + contact
        # Добавляем публикацию
        self.exec_update_query(f"""INSERT INTO {schema_name}.publications (tutor_id, fullname, institution, specialty, subject, contact, teach_experience, time_slot, pay_services)
                                   VALUES ('{tutor_id}', '{fullname}', '{institution}', '{specialty}', '{subject}', '{contact}', '{teach_experience}', '{time_slot}', '{pay_services}')""")


    def add_student(self, tg_id, fullname, contact):
        # Проверка, существует ли tg_id в таблице students
        existing_tutor = self.exec_query(f"""
            SELECT COUNT(*) FROM {schema_name}.students WHERE tg_id = {tg_id}
        """)

        # Если tg_id не найден, добавляем нового пользователя
        if existing_tutor[0][0] == 0:
            self.exec_update_query(f"""insert into {schema_name}.students (tg_id, fullname, contact)
                                                      values ('{tg_id}', '{fullname}', '{contact}')""")


    def add_tutor(self, tg_id, fullname):
        self.exec_update_query(f"""insert into {schema_name}.tutors (tg_id, fullname, is_recruiting)
                                          values ('{tg_id}', '{fullname}', '{True}')""")

    def add_request(self, student_id, tutor_id, publication_id, description):
        self.exec_update_query(f"""insert into {schema_name}.requests (student_id, tutor_id, publication_id, description)
                                          values ('{student_id}', '{tutor_id}', '{publication_id}', '{description}')""")

    #тестовый апдейт публикации
    def update_publication(self, tutor_id, fullname, institution, specialty, subject, teach_experience, time_slot, pay_services, contact):
        #contact = '@' + contact
        self.exec_update_query(f"""
            UPDATE {schema_name}.publications
            SET fullname = '{fullname}',
                institution = '{institution}',
                specialty = '{specialty}',
                subject = '{subject}',
                contact = '{contact}',
                teach_experience = '{teach_experience}',
                time_slot = '{time_slot}',
                pay_services = '{pay_services}'
            WHERE tutor_id = {tutor_id} AND subject = '{subject}' -- или другой критерий, который уникально идентифицирует запись
        """)

    # Функция для подсчета количества публикаций
    def get_publications_count(self):
        query = f"SELECT COUNT(*) FROM {schema_name}.publications"
        result = self.exec_query(query)
        return result[0][0]  # Возвращаем количество публикаций

    # Функция для получения публикаций для конкретной страницы
    def get_publications_for_page(self, page_number: int, per_page: int = 5):
        offset = (page_number - 1) * per_page  # Рассчитываем смещение для пагинации
        query = f"""
        SELECT * FROM {schema_name}.publications
        ORDER BY id ASC  -- Сортировка по id в порядке возрастания
        LIMIT {per_page} OFFSET {offset}  -- Ограничиваем количество публикаций для страницы
        """
        result = self.exec_query(query)
        return result

    # Функция для подсчета количества публикаций по фильтрам
    def get_filtered_publications_count(self, institution=None, specialty=None, subject=None, teach_experience=None,
                                        time_slot=None, pay_services=None):
        query = f"SELECT COUNT(*) FROM {schema_name}.publications WHERE TRUE"

        if institution:
            query += f" AND institution ILIKE '%{institution}%'"
        if specialty:
            query += f" AND specialty ILIKE '%{specialty}%'"
        if subject:
            query += f" AND subject ILIKE '%{subject}%'"
        if teach_experience:
            query += f" AND teach_experience ILIKE '%{teach_experience}%'"
        if time_slot:
            query += f" AND time_slot ILIKE '%{time_slot}%'"
        if pay_services:
            query += f" AND pay_services < '{pay_services}'"

        result = self.exec_query(query)
        return result[0][0]  # вернул количество совпадений


    # Функция для получения публикаций по фильтрам для конкретной страницы
    def get_publications_for_page_with_filters(self, page_number: int, per_page: int = 5, institution=None,
                                               specialty=None, subject=None, teach_experience=None, time_slot=None,
                                               pay_services=None):
        offset = (page_number - 1) * per_page  # Рассчитываем смещение для пагинации
        query = f"SELECT * FROM {schema_name}.publications WHERE TRUE"

        if institution:
            query += f" AND institution ILIKE '%{institution}%'"
        if specialty:
            query += f" AND specialty ILIKE '%{specialty}%'"
        if subject:
            query += f" AND subject ILIKE '%{subject}%'"
        if teach_experience:
            query += f" AND teach_experience ILIKE '%{teach_experience}%'"
        if time_slot:
            query += f" AND time_slot ILIKE '%{time_slot}%'"
        # if pay_services:
        #     query += f" AND pay_services ILIKE '%{pay_services}%'"
        if pay_services:
            query += f" AND pay_services < '{pay_services}'"

        query += f" ORDER BY id ASC LIMIT {per_page} OFFSET {offset}"  # Ограничиваю количество публикаций для страницы
        result = self.exec_query(query)
        return result


#db = DataBase()

#db.update_publication('5740628600','Олегов Олег Олегович', 'ЧелГУ', 'Программная инженерия', 'Информатика', 'Mihter_2208')