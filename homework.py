from http import HTTPStatus
import logging
from logging.handlers import RotatingFileHandler
import os
import requests
import sys
import time

from dotenv import load_dotenv
import telegram 

from exceptions import (TokenValidationError,
                       BadRequestError,
                       KeyAbsenceError,
                       WrongHomeworkDataTypeError,
                       WrongResponseDataTypeError,
                       UnknowVerdictError
                        )

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
handler = RotatingFileHandler('my_logger.log',
                              maxBytes=50000000,
                              backupCount=5,
                              encoding='UTF-8'
                              )
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def check_tokens() -> None:
    """Проверяет наличие необходимых токенов"""
    env_vars = [
        PRACTICUM_TOKEN,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID
    ]
    for token in env_vars:
        try:
            if token is None or token == '':
                raise TokenValidationError
        except TokenValidationError:
            logger.critical('Обязательные переменные окружения отсутствуют')
            sys.exit('Токен отсутствует')


def send_message(bot, message) -> None:
    """Отправляет сообщение пользователю в чат"""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        logger.error(f'Сбой при отправке сообщения в Telegram: {error}')
    else:
        logger.debug('Удачная отправка сообщения в Telegram')


def get_api_answer(timestamp: int) -> dict:
    """Производит запрос к API для получения статуса домашних работ"""
    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params={'from_date': timestamp}
        )
    except requests.RequestException as error:
        logger.error(f'Сбой при запросе к эндпоинту: {error}')
    if homework_statuses.status_code != HTTPStatus.OK:
        logger.error('Сбой при запросе к эндпоинту')
        raise BadRequestError   
    return homework_statuses.json()


def check_response(response: dict) -> dict:
    """Проверяет ответ API на соответствие документации"""
    if type(response) != dict:
        logger.error('Структура данных не соответствует ожиданиям')
        raise WrongResponseDataTypeError   
    if 'homeworks' not in response:
        logger.error('Ключ homework отсутствует')
        raise KeyAbsenceError
    if type(response['homeworks']) != list:
        logger.error('Данные под ключом homeworks пришли не в виде списка')
        raise WrongHomeworkDataTypeError
    return response


def parse_status(homework: dict) -> str:
    """Подготавливает сообщение с данными из ответа API"""
    if 'homework_name' not in homework:
        logger.error(f'Отсутствует ключ с названием работы')
        raise KeyAbsenceError
    homework_name = homework.get('homework_name')
    if homework.get('status') not in HOMEWORK_VERDICTS:
        logger.warning('Неожиданный статус домашней работы')
        raise UnknowVerdictError
    else:
        verdict = HOMEWORK_VERDICTS[homework.get('status')] 
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main() -> None:
    """Основная логика работы бота."""
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    curr_homework_status = ''
    while True:
        try:
            api_answer = get_api_answer(timestamp)
            checked_api_answer = check_response(api_answer)
            status_message = parse_status(checked_api_answer['homeworks'][0])

            if status_message != curr_homework_status:
                send_message(bot, status_message)
                curr_homework_status = status_message

        except Exception as error:
            logger.error(f'Сбой в работе программы: {error}')

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
