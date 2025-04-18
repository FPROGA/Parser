Resume Parser
Проект для автоматического анализа резюме с использованием NLP, PostgreSQL и интеграции с HH.ru

Этот инструмент помогает HR-специалистам и соискателям анализировать резюме, определять соответствие профессиям, выявлять недостающие навыки и находить подходящие вакансии.

📌 Функционал
✅ Анализ резюме (PDF/DOCX) – извлечение ключевых данных:
Имя,фамилия, хард скилы, софт скилы, время загрузки резюме
Оценка соответствия профессиям (в %).
Рекомендации по недостающим навыкам.

✅ Аналитика по всем загруженным резюме
Топ кандидатов по профессиям.
Лучшие навыки.
Статистика по навыкам и опыту.

✅ Интеграция с HH.ru
Поиск и анализ подходящих вакансий.
Сравнение требований вакансий с навыками кандидата.

🛠 Технологии
Backend: Python (Flask, NLP-библиотеки: spaCy, nltk, pdfplumber, python-docx)
Frontend: JavaScript ( JS + HTML/CSS)
База данных: PostgreSQL (хранение резюме и аналитики)
API: Интеграция с HH.ru (REST API)

Как это работает?
Загрузка резюме (PDF/DOCX) → парсинг текста.
NLP-обработка → извлечение сущностей (навыки, опыт, образование).
Сравнение с профессиями → расчет % соответствия.
Рекомендации → какие навыки нужно подтянуть.
Аналитика → сравнение кандидатов, топ резюме.
HH.ru API → подбор вакансий по навыкам.

🚀 Установка и запуск
1. Клонирование репозитория
git clone https://github.com/FPROGA/ResumeParser.git
cd ResumeParser

3. Настройка окружения
cd backend
-m pip install -r requirements.txt

Frontend
Просто откройте frontend/index.html в браузере (или запустите через Live Server в VS Code).

База данных (PostgreSQL)
Установите PostgreSQL и создайте БД:
CREATE DATABASE parser;
поменяйте имя и пароль пользователя, а также порт в файле database.py для своей базы данных

3. Запуск сервера
-m uvicorn app:app --reload        
