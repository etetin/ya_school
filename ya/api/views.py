from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser

from django.db import transaction
from django.db.models import Count
from django.db.models.functions import ExtractMonth
from collections import defaultdict

import numpy as np
from datetime import datetime, date
from dateutil import relativedelta

from ya.common.models import Citizen, Import
from ya.common.exception import WrongParams, CitizenNotExist, CitizenCantBeRelativeToHimself, ImportNotExist, \
    WrongRelativeData


def diff(first, second):
    second = set(second)
    return [item for item in first if item not in second]


def try_convert_date(date_):
    try:
        return datetime.strptime(date_, "%d.%m.%Y").strftime('%Y-%m-%d')
    except (ValueError, TypeError):
        return False


def convert_date(date_):
    return datetime.strptime(date_, "%d.%m.%Y").strftime('%Y-%m-%d')


def validator(citizens, full=True):
    for citizen in citizens:
        citizen_id = citizen.get('citizen_id', None)
        town = citizen.get('town', None)
        street = citizen.get('street', None)
        building = citizen.get('building', None)
        apartment = citizen.get('apartment', None)
        name = citizen.get('name', None)
        birth_date = citizen.get('birth_date', None)
        gender = citizen.get('gender', None)
        relatives = citizen.get('relatives', None)

        validation_data = {
            'citizen_id': {
                'value': citizen_id, 
                'conditions': [isinstance(citizen_id, int), ],
            },
            'town': {
                'value': town, 
                'conditions': [isinstance(town, str), ],
            },
            'street': {
                'value': street, 
                'conditions': [isinstance(street, str), ],
            },
            'building': {
                'value': building, 
                'conditions': [isinstance(building, str), ],
            },
            'apartment': {
                'value': apartment,
                'conditions': [isinstance(apartment, int), ],
            },
            'name': {
                'value': name,
                'conditions': [isinstance(name, str), ],
            },
            'birth_date': {
                'value': birth_date,
                'conditions': [
                    # validation that type this field is str included into function try_convert_date
                    (lambda date_: try_convert_date(date_))(birth_date),
                ],
            },
            'gender': {
                'value': gender, 
                'conditions': [
                    isinstance(gender, str),
                    gender in Citizen.GENDERS
                ],
            },
            'relatives': {
                'value': relatives, 
                'conditions': [
                    isinstance(relatives, list),
                    all(isinstance(relative_id, int) for relative_id in relatives) if relatives is not None and isinstance(relatives, list) else False
                ],
            },
        }

        for field in validation_data:
            if not full and validation_data[field]['value'] is None:
                continue

            if not all(condition for condition in validation_data[field]['conditions']):
                return False
    else:
        return True


@api_view(['POST', ])
@parser_classes([JSONParser])
def imports(request):
    if not isinstance(request.data, dict):
        raise WrongParams

    citizens = request.data.get('citizens', None)
    if not (isinstance(citizens, list) and validator(citizens=citizens)):
        raise WrongParams

    with transaction.atomic():
        import_id = Import.objects.create().id

    citizens_relatives = {}
    db_citizens = []
    for citizen_data in citizens:
        citizens_relatives[citizen_data['citizen_id']] = citizen_data['relatives']

        db_citizens.append(
            Citizen(
                import_id=import_id,
                citizen_id=citizen_data['citizen_id'],
                town=citizen_data['town'],
                street=citizen_data['street'],
                building=citizen_data['building'],
                apartment=citizen_data['apartment'],
                name=citizen_data['name'],
                birth_date=convert_date(citizen_data['birth_date']),
                gender=citizen_data['gender'],
                relatives=citizen_data['relatives'],
            )
        )

    for citizen_id in citizens_relatives:
        try:
            # citizen can't be relative to himself
            if not all(
                citizen_id in citizens_relatives[citizen_relative_id] and citizen_relative_id != citizen_id
                for citizen_relative_id in citizens_relatives[citizen_id]
            ):
                raise WrongRelativeData
        except KeyError:
            raise WrongRelativeData

    Citizen.objects.bulk_create(db_citizens)

    response = {
        'data': {
            'import_id': import_id
        }
    }

    return Response(response, status=201)


@api_view(['PATCH', ])
@parser_classes([JSONParser])
def import_change(request, import_id, citizen_id):
    if not isinstance(request.data, dict):
        raise WrongParams

    try:
        citizen = Citizen.objects.get(import_id=import_id, citizen_id=citizen_id)
    except Citizen.DoesNotExist:
        raise CitizenNotExist

    valid_citizens_data = validator(citizens=[request.data], full=False)
    if not valid_citizens_data:
        raise WrongParams

    town = request.data.get('town', None)
    street = request.data.get('street', None)
    building = request.data.get('building', None)
    apartment = request.data.get('apartment', None)
    name = request.data.get('name', None)
    birth_date = request.data.get('birth_date', None)
    gender = request.data.get('gender', None)
    relatives = request.data.get('relatives', None)

    # citizen can't be relative to himself
    if relatives is not None and citizen_id in relatives:
        raise CitizenCantBeRelativeToHimself

    # It's normal way to set attrs like this???
    # fields = ['town', 'street', 'building', 'apartment', 'name', 'birth_date', 'gender', 'relatives']
    # for field in fields:
    #     data = request.data.get(field, None)
    #     if data is not None:
    #         citizen.__setattr__(field, data)

    if town is not None:
        citizen.town = town
    if street is not None:
        citizen.street = street
    if building is not None:
        citizen.building = building
    if apartment is not None:
        citizen.apartment = apartment
    if name is not None:
        citizen.name = name
    if birth_date is not None:
        citizen.birth_date = convert_date(birth_date)
    if gender is not None:
        citizen.gender = gender
    if relatives is not None:
        try:
            with transaction.atomic():
                for relative_citizen_id in diff(relatives, citizen.relatives):
                    relative_citizen = Citizen.objects.get(import_id=import_id, citizen_id=relative_citizen_id)
                    relative_citizen.relatives.append(citizen_id)
                    relative_citizen.save()

                for relative_citizen_id in diff(citizen.relatives, relatives):
                    relative_citizen = Citizen.objects.get(import_id=import_id, citizen_id=relative_citizen_id)
                    relative_citizen.relatives.remove(citizen_id)
                    relative_citizen.save()

                citizen.relatives = relatives
        except (ValueError, Citizen.DoesNotExist):
            raise WrongRelativeData

    if any(field is not None for field in [town, street, building, apartment, name, birth_date, gender, relatives]):
        citizen.save()

    return Response({
            'data': {
                'import_id': import_id
            }
        },
        status=200
    )


@api_view(['GET', ])
def import_data(request, import_id):
    result = {
        'data': []
    }

    citizens = Citizen.objects.filter(import_id=import_id)
    if len(citizens) == 0:
        raise ImportNotExist

    for citizen in citizens:
        citizen_data = {
            "citizen_id": citizen.citizen_id,
            "town": citizen.town,
            "street": citizen.street,
            "building": citizen.building,
            "apartment": citizen.apartment,
            "name": citizen.name,
            "birth_date": citizen.birth_date.strftime("%d.%m.%Y"),
            "gender": citizen.gender,
            "relatives": citizen.relatives,
        }
        result['data'].append(citizen_data)

    return Response(result, status=200)


@api_view(['GET', ])
def import_birthdays(request, import_id):
    citizens = Citizen.objects.filter(import_id=import_id)
    if len(citizens) == 0:
        raise ImportNotExist

    result = {
        'data': {
            str(num): []
            for num in range(1, 12 + 1)
        }
    }

    for citizen in citizens:
        tt = citizens.filter(citizen_id__in=citizen.relatives) \
            .annotate(month=ExtractMonth('birth_date')) \
            .values('month') \
            .annotate(count=Count('id'))\
            .values('month', 'count')

        for t in tt:
            result['data'][str(t["month"])].append({
                'citizen_id': citizen.citizen_id,
                'count': int(t["count"])
            })

    return Response(result, status=200)


@api_view(['GET', ])
def import_birthdays_age(request, import_id):
    result = {'data': []}
    data = defaultdict(lambda: [])

    current_date = date.today()
    # TODO is it possible to optimize the queryset? (move all calculation into db)
    citizens = Citizen.objects.filter(import_id=import_id).values_list('town', 'birth_date')

    if len(citizens) == 0:
        raise ImportNotExist

    for citizen_data in citizens:
        years = relativedelta.relativedelta(current_date, citizen_data[1]).years
        data[citizen_data[0]].append(years)

    for town in data:
        town_percentiles = {'town': town}
        for percentile in [50, 75, 99]:
            # TODO probable need to apply math.ceil?
            town_percentiles[f'p{percentile}'] = np.percentile(np.array(data[town]), percentile)

        result['data'].append(town_percentiles)

    return Response(result, status=200)
