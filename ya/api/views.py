from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.db import transaction
from django.db.models import Max, Count
from django.db.models.functions import ExtractMonth

import json
import math
from datetime import datetime, date
from dateutil import relativedelta

from ya.common.models import Citizen


def diff(first, second):
    second = set(second)
    return [item for item in first if item not in second]


def try_convert_date(date):
    try:
        return datetime.strptime(date, "%d.%m.%Y").strftime('%Y-%m-%d')
    except (ValueError, TypeError) as err:
        return False


def convert_date(date):
    return datetime.strptime(date, "%d.%m.%Y").strftime('%Y-%m-%d')


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
                'conditions': [isinstance(citizen_id, int),],
            },
            'town': {
                'value': town, 
                'conditions': [isinstance(town, str),],
            },
            'street': {
                'value': street, 
                'conditions': [isinstance(street, str),],
            },
            'building': {
                'value': building, 
                'conditions': [isinstance(building, str),],
            },
            'apartment': {
                'value': apartment,
                'conditions': [isinstance(apartment, int),],
            },
            'name': {
                'value': name,
                'conditions': [isinstance(name, str),],
            },
            'birth_date': {
                'value': birth_date,
                'conditions': [
                    # validation that type this field is str included into function try_convert_date
                    (lambda date: try_convert_date(date))(birth_date),
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


@api_view(['POST',])
def imports(request):
    data = json.loads(request.body.decode('utf-8'))

    citizens = data.get('citizens', None)
    if not isinstance(citizens, list):
        return Response(status=400)

    valid_citizens_data = validator(citizens=citizens)
    if not valid_citizens_data:
        return Response(status=400)

    with transaction.atomic():
        last_import = Citizen.objects.aggregate(max_value=Max('import_id'))
        if last_import['max_value'] is None:
            import_id = 1
        else:
            import_id = last_import['max_value'] + 1

    for citizen_data in citizens:
        Citizen.objects.create(
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

    response = {
        'data': {
            'import_id': import_id
        }
    }

    return Response(response, status=201)


@api_view(['PATCH',])
def import_change(request, import_id, citizen_id):
    try:
        citizen = Citizen.objects.get(import_id=import_id, citizen_id=citizen_id)
    except Citizen.DoesNotExist:
        return Response(status=404)

    valid_citizens_data = validator(citizens=[request.data], full=False)
    if not valid_citizens_data:
        return Response(status=400)

    town = request.data.get('town', None)
    street = request.data.get('street', None)
    building = request.data.get('building', None)
    apartment = request.data.get('apartment', None)
    name = request.data.get('name', None)
    birth_date = request.data.get('birth_date', None)
    gender = request.data.get('gender', None)
    relatives = request.data.get('relatives', None)

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
            return Response(status=400)

    if any(field is not None for field in [town, street, building, apartment, name, birth_date, gender, relatives]):
        citizen.save()

    return Response({
            'data': {
                'import_id': import_id
            }
        },
        status=200
    )


@api_view(['GET',])
def import_data(request, import_id):
    result = {
        'data': []
    }

    for citizen in Citizen.objects.filter(import_id=import_id):
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


@api_view(['GET',])
def import_birthdays(request, import_id):
    result = {
        'data': {}
    }

    for num in range(1, 13):
        result['data'][str(num)] = []

    print(result)

    citizens = Citizen.objects.filter(import_id=import_id)
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


@api_view(['GET',])
def import_birthdays_age(request, import_id):
    result = {}
    data = {}

    # TODO Probably this is not best solution
    percentiles = [50, 75, 99]

    current_date = date.today()
    citizens = Citizen.objects.filter(import_id=import_id)
    for citizen in citizens:
        stat = data.get(citizen.town, {
            'p50': 0,
            'p75': 0,
            'p99': 0,
            'all': 0,
        })
        years = relativedelta.relativedelta(current_date, citizen.birth_date).years
        for percentile in percentiles:
            if years < percentile:
                stat[f'p{percentile}'] += 1
                stat['all'] += 1

        data[citizen.town] = stat

    # TODO need to make this implementation like numpy.percentiles and check that all calculate is correctly
    result['data'] = [
        {
            'town': town,
            'p50': math.ceil(data[town]['p50'] / data[town]['all']) * 100,
            'p75': math.ceil(data[town]['p75'] / data[town]['all']) * 100,
            'p99': math.ceil(data[town]['p99'] / data[town]['all']) * 100,
        } for town in data
    ]

    '''
    # Way more better?
    # TODO try to convert into Django QuerySet
    
    # UPD
    # This solution do not cover some cases, for example when in import all citizen older then 99 years
    # TODO Come back later
    raw_query = """
        SELECT
            SUM(citizen_under_an_age.count) AS count,
            town as id
        FROM (
            SELECT
               COUNT(*) as count,
               town, 
               birth_date
            FROM common_citizen
            WHERE import_id=""" + str(import_id) + """
            GROUP BY town, birth_date
            HAVING date_part('year', age('2019-08-02', birth_date)) < <AGE>
        ) AS citizen_under_an_age
        GROUP BY town;    
    """


    percentiles = [50, 75, 99]
    data = {}
    common_count = Citizen.objects.filter(import_id=import_id).count()

    for percentile in percentiles:
        stat_by_towns = Citizen.objects.raw(raw_query=raw_query.replace('<AGE>', str(percentile)))
        for town in stat_by_towns:
            if town.id not in data:
                data[town.id] = {}

            data[town.id][f'p{percentile}'] = town.count

    r = []
    for town in data:
        data[town]['town'] = town
        r.append(data[town])

    result['data'] = r
    '''

    return Response(result, status=200)