import os

import psycopg2 as ps

from database.config import host, user, password, db_name, schema_name


class DataBase:
    def __init__(self):
        self.connection = 0


    #Соединение с бд
    def connect(self):
        try:
            self.connection = ps.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
            )
            self.connection.autocommit = True
        except Exception as e:
            print(f"[INFO] Error while connecting to PostgreSQL: {e}")


    # Выполнение SQL-запроса
    def exec_query(self, update, info_message, is_all_strs=False):
        try:
            # Подключаемся к БД
            connection = ps.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
            )
            connection.autocommit = True
            with connection.cursor() as cursor:
                # Выполняем SQL-запрос
                cursor.execute(update)
                print(info_message)
                if is_all_strs:
                    result = cursor.fetchall()
                else:
                    result = cursor.fetchone()
            return result
        except Exception as _ex:
            print("[INFO] Error while working with PostgreSQL", _ex)
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgreSQL connection closed")


     # Добавление нового пользователя
    #def add_publication(self, tutor_id, fullname, institution, specialty, subject, contact):
    #    contact = '@'+contact
    #    self.exec_query(f"""insert into {schema_name}.publications (tutor_id, fullname, institution, specialty, subject, contact)
    #                                   values ('{tutor_id}', '{fullname}', '{institution}', '{specialty}', '{subject}', '{contact}')""",
    #                 "[INFO] Tutor was added", False)