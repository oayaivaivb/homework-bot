from http import HTTPStatus
import logging
import os
import time

import requests
from dotenv import load_dotenv
from telebot import TeleBot, apihelper


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


logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
stream_handler = logging.StreamHandler()

stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def check_tokens():
    """Проверяет доступность переменных окружения."""
    tokens = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }

    missing_tokens = [
        name for name, value in tokens.items()
        if not value
    ]

    if missing_tokens:
        logger.critical(f'Отсутствуют необходимые токены: {missing_tokens}')
        return False

    return True


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(f'Отправлено сообщение: {message}')
        return True
    except apihelper.ApiException as error:
        logger.error(f'Ошибка при отправке сообщения: {error}')
        return False
    except requests.RequestException as error:
        logger.error(f'Ошибка при запросе к Telegram API: {error}')
        return False


def get_api_answer(timestamp):
    """
    Делает запрос к единственному эндпоинту API-сервиса.
    В качестве параметра запроса передает временную метку.
    Если запрос к API-сервису прошел успешно, должен вернуть ответ API,
    преобразовав его из формата JSON к типам данных Python.
    """
    payload = {'from_date': int(timestamp)}
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=payload
        )

    except requests.RequestException as error:
        raise ConnectionError(
            f'Ошибка при запросе к API: {error}'
            f' по адресу: {ENDPOINT}'
            f' c заголовками: {HEADERS}'
            f' и параметрами: {payload}'
        )

    if response.status_code != HTTPStatus.OK:
        raise ConnectionError(f'Ответ API не 200: {response.status_code}')

    return response.json()


def check_response(response):
    """
    Проверяет ответ API на корректность.
    Если ответ API соответствует ожиданиям,
    должен вернуть список домашних работ.
    """
    if not isinstance(response, dict):
        raise TypeError(
            f'Ответ API должен быть словарем, а получен {type(response)}')

    if 'homeworks' not in response:
        raise KeyError('В ответе API нет ключа "homeworks"')

    homeworks = response['homeworks']

    if not isinstance(homeworks, list):
        raise TypeError(
            f'Ответ API "homeworks" должен быть списком,'
            f' а получен {type(homeworks)}')

    return homeworks


def parse_status(homework):
    """Извлекает статус домашней работы из информации о ней."""
    if 'homework_name' not in homework:
        raise KeyError('В ответе API нет ключа "homework_name"')
    homework_name = homework['homework_name']

    if 'status' not in homework:
        raise KeyError('В ответе API нет ключа "status"')
    homework_status = homework['status']

    if homework_status not in HOMEWORK_VERDICTS:
        raise ValueError(
            f'Неизвестный статус домашней работы: {homework_status}')

    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def handle_main_error(error, bot, last_status):
    """Обрабатывает ошибки в основном цикле."""
    message = f'Сбой в работе программы: {error}'
    if message != last_status:
        if send_message(bot, message):
            last_status = message
            logger.error(message)
    return last_status


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Отсутствуют необходимые токены')
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
                    if send_message(bot, message):
                        last_status = message
                        logger.debug(f'Отправлено сообщение: {message}')
                else:
                    logger.debug('Статус домашней работы не изменился')

            except (KeyError, IndexError):
                logger.debug('Нет домашних работ для обработки')

            timestamp = response.get('current_date', timestamp)

        except Exception as error:
            last_status = handle_main_error(error, bot, last_status)

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
