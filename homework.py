import logging
import os
import time

import requests
from dotenv import load_dotenv
from telebot import TeleBot


load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.DEBUG,
    handlers=[logging.StreamHandler()]
)


def check_tokens():
    """Проверяет доступность переменных окружения."""
    if not PRACTICUM_TOKEN:
        logging.critical('Отсутствует токен PRACTICUM_TOKEN')
        return False

    if not TELEGRAM_TOKEN:
        logging.critical('Отсутствует токен TELEGRAM_TOKEN')
        return False

    if not TELEGRAM_CHAT_ID:
        logging.critical('Отсутствует токен TELEGRAM_CHAT_ID')
        return False

    return True


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug(f'Отправлено сообщение: {message}')
    except Exception as error:
        logging.error(f'Ошибка при отправке сообщения: {error}')


def get_api_answer(timestamp):
    """
    Делает запрос к единственному эндпоинту API-сервиса.
    В качестве параметра запроса передает временную метку.
    Если запрос к API-сервису прошел успешно, должен вернуть ответ API,
    преобразовав его из формата JSON к типам данных Python.
    """
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params={'from_date': int(timestamp)}
        )

    except requests.RequestException as error:
        logging.error(f'Ошибка при запросе к API: {error}')
        raise ConnectionError(f'Ошибка при запросе к API: {error}')

    if response.status_code != 200:
        logging.error(f'Ответ API не 200: {response.status_code}')
        raise ConnectionError(f'Ответ API не 200: {response.status_code}')

    try:
        response_json = response.json()
    except ValueError as error:
        logging.error(f'Ошибка при преобразовании ответа API в JSON: {error}')
        raise ValueError(
            f'Ошибка при преобразовании ответа API в JSON: {error}')

    return response_json


def check_response(response):
    """
    Проверяет ответ API на корректность.
    Если ответ API соответствует ожиданиям,
    должен вернуть список домашних работ.
    """
    if not isinstance(response, dict):
        logging.error('Ответ API не словарь')
        raise TypeError('Ответ API не словарь')

    try:
        homeworks = response['homeworks']
    except KeyError:
        logging.error('В ответе API нет ключа "homeworks"')
        raise KeyError('В ответе API нет ключа "homeworks"')

    if not isinstance(homeworks, list):
        logging.error('Ответ API "homeworks" не список')
        raise TypeError('Ответ API "homeworks" не список')

    return homeworks


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе статус работы."""
    try:
        homework_name = homework['homework_name']
    except KeyError:
        logging.error('В ответе API нет ключа "homework_name"')
        raise KeyError('В ответе API нет ключа "homework_name"')

    try:
        homework_status = homework['status']
    except KeyError:
        logging.error('В ответе API нет ключа "status"')
        raise KeyError('В ответе API нет ключа "status"')

    if homework_status not in HOMEWORK_VERDICTS:
        logging.error(f'Неизвестный статус домашней работы: {homework_status}')
        raise ValueError(
            f'Неизвестный статус домашней работы: {homework_status}')

    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logging.critical('Отсутствуют необходимые токены')
        return

    bot = TeleBot(TELEGRAM_TOKEN)

    timestamp = int(time.time())

    last_status = None

    while True:
        try:
            response = get_api_answer(timestamp)

            check_response(response)

            try:
                message = parse_status(response['homeworks'][0])

                if message != last_status:
                    last_status = message
                    send_message(bot, message)
                    logging.debug(f'Отправлено сообщение: {message}')
                else:
                    logging.debug('Статус домашней работы не изменился')

            except (KeyError, IndexError):
                logging.debug('Нет домашних работ для обработки')

            timestamp = response.get('current_date', timestamp)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            logging.error(message)

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
