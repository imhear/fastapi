class AppException(Exception):
    pass


class ResourceNotFound(AppException):
    pass


class BadRequest(AppException):
    pass