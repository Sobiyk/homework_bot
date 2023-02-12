class TokenValidationError(Exception):
    """Ошибка при отсутствии необохдимых токенов."""

    def __str__(self) -> str:
        return 'Отсутствуют необходимые переменные окружения'


class BadRequestError(Exception):
    """Сбой при запросе к эндпоинту."""

    def __str__(self) -> str:
        return 'Сбой при запросе к эндпоинту'


class KeyAbsenceError(Exception):
    """Ошибка при отсутствии необохдимых ключей в ответе API."""

    def __str__(self) -> str:
        return 'Отсутствует ключ с названием работы'


class WrongHomeworkDataTypeError(TypeError):
    """Неверный тип данных ключа homeworks в ответе API."""

    def __str__(self) -> str:
        return 'Отсутствует ключ с названием работы'


class WrongResponseDataTypeError(TypeError):
    """Неверный тип данных ответа API."""

    def __str__(self) -> str:
        return 'Отсутствует ключ с названием работы'


class UnknowVerdictError(KeyError):
    """Ошибка при получении неожиданного вердикта домашней работы."""

    def __str__(self) -> str:
        return 'Неожиданный вердикт домашней работы'
