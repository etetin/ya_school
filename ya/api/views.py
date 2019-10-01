from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser

from django.db import transaction
from django.db.models import Count
from django.db.models.functions import ExtractMonth

import numpy as np
import json
from datetime import datetime, date
from dateutil import relativedelta
from collections import defaultdict

from ya.common.models import Citizen, Import
from ya.common.exception import WrongParams, CitizenNotExist, ImportNotExist, \
    WrongRelativeData, DuplicateCitizenId
from ya.common.validator import Validator


def diff(first, second):
    second = set(second)
    return [item for item in first if item not in second]


@api_view(['POST', ])
@parser_classes([JSONParser])
def imports(request):
    if not isinstance(request.data, dict):
        raise WrongParams

    citizens = request.data.get('citizens', None)
    Validator.validate_citizens_data(citizens)

    new_import = Import()
    import_id = new_import.create()
    new_import.set_citizens(citizens_data=citizens)

    response = {
        'data': {
            'import_id': import_id
        }
    }

    return Response(response, status=201)

#
# @api_view(['PATCH', ])
# @parser_classes([JSONParser])
# def import_change(request, import_id, citizen_id):
#     if (isinstance(request.data, dict) and len(request.data) == 0) or \
#             request.data.get('citizen_id') is not None:
#         raise WrongParams
#
#     fields = ['town', 'street', 'building', 'apartment', 'name', 'birth_date', 'gender', 'relatives']
#     for field in fields:
#         if field in request.data and request.data[field] is None:
#             raise WrongParams
#
#     try:
#         citizen = Citizen.objects.get(import_id=import_id, citizen_id=citizen_id)
#     except Citizen.DoesNotExist:
#         raise CitizenNotExist
#
#     valid_citizens_data = validator(citizens=[request.data], full=False)
#     if not valid_citizens_data:
#         raise WrongParams
#
#     for field in fields:
#         value = request.data.get(field, None)
#         if value is not None:
#             if field == 'relatives':
#                 try:
#                     with transaction.atomic():
#                         for relative_citizen_id in diff(value, citizen.relatives):
#                             relative_citizen = Citizen.objects.get(import_id=import_id, citizen_id=relative_citizen_id)
#                             relative_citizen.relatives.append(citizen_id)
#                             relative_citizen.save()
#
#                         for relative_citizen_id in diff(citizen.relatives, value):
#                             relative_citizen = Citizen.objects.get(import_id=import_id, citizen_id=relative_citizen_id)
#                             relative_citizen.relatives.remove(citizen_id)
#                             relative_citizen.save()
#                 except (ValueError, Citizen.DoesNotExist):
#                     raise WrongRelativeData
#             elif field == 'birth_date':
#                 value = convert_date(value)
#
#             setattr(citizen, field, value)
#     else:
#         citizen.save()
#
#     return Response({
#             'data': citizen.get_data()
#         },
#         status=200
#     )
#
#
@api_view(['GET', ])
def import_data(request, import_id):
    import_ = Import(import_id=import_id)

    result = {
        'data': import_.get_data()
    }

    return Response(result, status=200)


# @api_view(['GET', ])
# def import_birthdays(request, import_id):
#     citizens = Citizen.objects.filter(import_id=import_id)
#     if len(citizens) == 0:
#         raise ImportNotExist
#
#     result = {
#         'data': {
#             str(num): []
#             for num in range(1, 12 + 1)
#         }
#     }
#
#     for citizen in citizens:
#         tt = citizens.filter(citizen_id__in=citizen.relatives) \
#             .annotate(month=ExtractMonth('birth_date')) \
#             .values('month') \
#             .annotate(count=Count('id'))\
#             .values('month', 'count')
#
#         for t in tt:
#             result['data'][str(t["month"])].append({
#                 'citizen_id': citizen.citizen_id,
#                 'count': int(t["count"])
#             })
#
#     return Response(result, status=200)
#
#
# @api_view(['GET', ])
# def import_town_stat(request, import_id):
#     result = {'data': []}
#     data = defaultdict(lambda: [])
#
#     current_date = date.today()
#     # TODO is it possible to optimize the queryset? (move all calculation into db)
#     citizens = Citizen.objects.filter(import_id=import_id).values_list('town', 'birth_date')
#
#     if len(citizens) == 0:
#         raise ImportNotExist
#
#     for citizen_data in citizens:
#         years = relativedelta.relativedelta(current_date, citizen_data[1]).years
#         data[citizen_data[0]].append(years)
#
#     for town in data:
#         town_percentiles = {'town': town}
#         for percentile in [50, 75, 99]:
#             town_percentiles[f'p{percentile}'] = round(np.percentile(np.array(data[town]), percentile), 2)
#
#         result['data'].append(town_percentiles)
#
#     return Response(result, status=200)
