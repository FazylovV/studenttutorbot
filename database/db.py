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
    def add_publication(self, tutor_id, fullname, institution, specialty, subject, contact):
        # Проверка, существует ли tutor_id в таблице tutors
        existing_tutor = self.exec_query(f"""
            SELECT COUNT(*) FROM {schema_name}.tutors WHERE tg_id = {tutor_id}
        """)

        # Если tutor_id не найден, добавляем нового пользователя
        if existing_tutor[0][0] == 0:
            self.add_tutor(tutor_id, fullname)

        contact = '@' + contact
        # Добавляем публикацию
        self.exec_update_query(f"""INSERT INTO {schema_name}.publications (tutor_id, fullname, institution, specialty, subject, contact)
                                   VALUES ('{tutor_id}', '{fullname}', '{institution}', '{specialty}', '{subject}', '{contact}')""")


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


    def update_publication(self, tutor_id, fullname, institution, specialty, subject, contact):
        contact = '@' + contact
        self.exec_update_query(f"""
            UPDATE {schema_name}.publications
            SET fullname = '{fullname}',
                institution = '{institution}',
                specialty = '{specialty}',
                subject = '{subject}',
                contact = '{contact}'
            WHERE tutor_id = {tutor_id} AND subject = '{subject}' -- или другой критерий, который уникально идентифицирует запись
        """)

#db = DataBase()

#db.update_publication('5740628600','Олегов Олег Олегович', 'ЧелГУ', 'Программная инженерия', 'Информатика', 'Mihter_2208')