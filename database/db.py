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


    # Добавление нового пользователя
    def add_student(self, id, tg_id, fullname, contact):
        self.exec_update_query(f"""insert into {schema_name}.students (id, tg_id, fullname, contact)
                                          values ('{id}', '{tg_id}', '{fullname}', '{contact}')""")

db = DataBase()
db.add_student(2, 2, '2', '2')