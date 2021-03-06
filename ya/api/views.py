from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser

import numpy as np
import json
from datetime import datetime, date
from dateutil import relativedelta
from collections import defaultdict

from ya.common.models import Citizen, Import
from ya.common.validator import Validator


def diff(first, second):
    second = set(second)
    return [item for item in first if item not in second]


@api_view(['POST', ])
@parser_classes([JSONParser])
def imports(request):
    Validator.validate_citizens_data(data=request.data)

    citizens = request.data.get('citizens', None)

    new_import = Import()
    new_import.set_citizens(citizens_data=citizens)

    response = {
        'data': {
            'import_id': new_import.import_id
        }
    }

    return Response(response, status=201)


@api_view(['PATCH', ])
@parser_classes([JSONParser])
def import_change(request, import_id, citizen_id):
    citizen = Citizen(import_id=import_id, citizen_id=citizen_id)

    Validator.validate_citizen_data_for_update(data=request.data)
    citizen_data = citizen.update(data=request.data)

    return Response({
            'data': citizen_data
        },
        status=200
    )


@api_view(['GET', ])
def import_data(request, import_id):
    import_ = Import(import_id=import_id)

    result = {
        'data': import_.get_data()
    }

    return Response(result, status=200)


@api_view(['GET', ])
def import_birthdays(request, import_id):
    import_ = Import(import_id=import_id)
    citizens = import_.get_data(to_dict=True)

    data = {
        str(num): defaultdict(int)
        for num in range(1, 12 + 1)
    }

    for citizen_id in citizens:
        for relative_citizen_id in citizens[citizen_id]['relatives']:
            month = citizens[relative_citizen_id]['birth_date'][3:5]
            data[month][citizen_id] += 1

    result = {
        'data': {
            month: [
                {
                    'citizen_id': citizen_id,
                    'presents': data[month][citizen_id]
                }
                for citizen_id in data[month]
            ]
            for month in data
        }
    }

    return Response(result, status=200)


@api_view(['GET', ])
def import_town_stat(request, import_id):
    import_ = Import(import_id=import_id)
    citizens = import_.get_data()

    result = {'data': []}
    data = defaultdict(lambda: [])

    current_date = date.today()
    for citizen_data in citizens:
        years = relativedelta.relativedelta(
            current_date,
            datetime.strptime(citizen_data['birth_date'], '%d.%m.%Y')
        ).years
        data[citizen_data['town']].append(years)

    for town in data:
        town_percentiles = {'town': town}
        for percentile in [50, 75, 99]:
            town_percentiles[f'p{percentile}'] = round(np.percentile(np.array(data[town]), percentile), 2)

        result['data'].append(town_percentiles)

    return Response(result, status=200)
