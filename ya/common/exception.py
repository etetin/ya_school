from __future__ import annotations

from typing import List

from rest_framework.exceptions import APIException, NotFound, ParseError
from rest_framework.views import exception_handler


def custom_exception_handler(exc: APIException, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            'status': False,
            'code': exc.default_code,
            'message': exc.detail,
        }

    return response


class WrongParams(ParseError):
    status_code = 400
    default_detail = 'Неверные параметры запроса'


class DuplicateCitizenId(ParseError):
    status_code = 400
    default_detail = 'Дубликат граждан'


class WrongRelativeData(ParseError):
    status_code = 400
    default_detail = 'Неверные параметры запроса'


class CitizenNotExist(NotFound):
    status_code = 404
    default_detail = 'Гражданин не найден'


class ImportNotExist(NotFound):
    status_code = 404
    default_detail = 'Импорт'
