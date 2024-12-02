CREATE DATABASE tutordb;

-- Создание таблицы tutors
CREATE TABLE "tutors" (
    "id" SERIAL NOT NULL,           -- Автоинкрементный id для tutor
    "tg_id" BIGINT NOT NULL,        -- tg_id как идентификатор
    "fullname" TEXT NOT NULL,       -- Поле для имени
    "is_recruiting" BOOLEAN NOT NULL, -- Флаг рекрутинга
    PRIMARY KEY ("tg_id")           -- tg_id как PRIMARY KEY
);

-- Создание таблицы publications
CREATE TABLE "publications" (
    "id" SERIAL NOT NULL,           -- Автоинкрементный id для publication
    "tutor_id" BIGINT NOT NULL,     -- Ссылка на tutor
    "fullname" TEXT NOT NULL,       -- Поле для имени
    "institution" TEXT NOT NULL,    -- Поле для института
    "specialty" TEXT NOT NULL,      -- Поле для специальности
    "subject" TEXT NOT NULL,        -- Поле для предмета
    "contact" TEXT NOT NULL,        -- Поле для контакта
    PRIMARY KEY ("id"),             -- id как PRIMARY KEY
    CONSTRAINT "publications_tutor_id_foreign" FOREIGN KEY ("tutor_id") REFERENCES "tutors"("tg_id") ON DELETE CASCADE  -- Ссылка на tg_id в tutors
);

-- Создание таблицы students
CREATE TABLE "students" (
    "id" SERIAL NOT NULL,           -- Автоинкрементный id для student
    "tg_id" BIGINT NOT NULL,        -- tg_id как идентификатор
    "fullname" TEXT NOT NULL,       -- Поле для имени
    "contact" TEXT NOT NULL,        -- Поле для контакта
    PRIMARY KEY ("tg_id")           -- tg_id как PRIMARY KEY
);

-- Создание таблицы requests
CREATE TABLE "requests" (
    "id" SERIAL NOT NULL,           -- Автоинкрементный id для запроса
    "student_id" BIGINT NOT NULL,   -- Ссылка на студента
    "tutor_id" BIGINT NOT NULL,     -- Ссылка на преподавателя
    "publication_id" BIGINT NOT NULL, -- Ссылка на публикацию
    "description" TEXT NOT NULL,
    "isAccepted" BOOLEAN NOT NULL DEFAULT '0', -- Статус запроса
    PRIMARY KEY ("id"),             -- id как PRIMARY KEY
    CONSTRAINT "requests_tutor_id_foreign" FOREIGN KEY ("tutor_id") REFERENCES "tutors"("tg_id") ON DELETE CASCADE,  -- Ссылка на tg_id в tutors
    CONSTRAINT "requests_student_id_foreign" FOREIGN KEY ("student_id") REFERENCES "students"("tg_id") ON DELETE CASCADE, -- Ссылка на tg_id в students
    CONSTRAINT "requests_publication_id_foreign" FOREIGN KEY ("publication_id") REFERENCES "publications"("id") ON DELETE CASCADE -- Ссылка на id в publications
);