class TokenValidationError(Exception):
    pass


class BadRequestError(Exception):
    pass


class KeyAbsenceError(Exception):
    pass


class WrongHomeworkDataTypeError(TypeError):
    pass


class WrongResponseDataTypeError(TypeError):
    pass


class UnknowVerdictError(KeyError):
    pass
