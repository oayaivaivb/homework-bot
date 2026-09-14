# 🤖 Homework Bot — Telegram-бот

**Homework Bot** — Telegram-бот на Python для автоматического отслеживания статуса домашних работ через API сервиса Практикум Домашка.

Бот периодически проверяет статус работы и отправляет уведомление в Telegram, если статус изменился.

## ✨ Основные возможности

* 📡 Получение статуса домашней работы через API
* ⏱️ Автоматическая проверка каждые 10 минут
* 💬 Уведомления в Telegram при изменении статуса
* 🚫 Защита от повторных уведомлений
* 📝 Логирование событий и ошибок
* 🔐 Работа с токенами через переменные окружения
* 🧪 Автоматические тесты

## 🛠 Технологии

* **Python 3**
* **Requests**
* **pyTelegramBotAPI**
* **python-dotenv**
* **pytest**
* **Flake8**

## 🔐 Настройка

Создайте файл `.env` в корне проекта:

```env
PRACTICUM_TOKEN=your_practicum_token
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

## 🚀 Запуск проекта

Клонируйте репозиторий:

```bash
git clone https://github.com/oayaivaivb/homework-bot.git
cd homework-bot
```

Создайте виртуальное окружение:

```bash
python -m venv venv
```

**Windows:**

```bash
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

Установите зависимости:

```bash
pip install -r requirements.txt
```

Запустите бота:

```bash
python homework.py
```

## 🧪 Тестирование

```bash
pytest
```

Проверка качества кода:

```bash
flake8
```

## 📁 Структура проекта

```text
homework-bot/
├── tests/
├── homework.py
├── requirements.txt
├── Procfile
├── pytest.ini
├── setup.cfg
├── .gitignore
├── LICENSE
└── README.md
```

## 🎯 О проекте

Проект выполнен в рамках обучения backend-разработке на Python и демонстрирует работу с внешним API, Telegram Bot API, логированием, обработкой ошибок и переменными окружения.
