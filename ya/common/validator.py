from datetime import datetime

from ya.common.exception import WrongParams, CitizenNotExist, ImportNotExist, \
    WrongRelativeData, DuplicateCitizenId
from ya.common.models import Citizen


def try_convert_date(date_):
    try:
        # it's strange that strptime(date_, "%d.%m.%Y") correctly work with  days and months without padding zero
        if date_ is not None and len(date_) != 10:
            return False

        return datetime.strptime(date_, "%d.%m.%Y")
    except (ValueError, TypeError):
        return False


class Validator:
    @staticmethod
    def validate_fields(citizens, full=True):
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
                        all(isinstance(relative_id, int) for relative_id in
                            relatives) if relatives is not None and isinstance(relatives, list) else False
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

    @staticmethod
    def validate_citizens_data(citizens_data):
        if not (isinstance(citizens_data, list) and Validator.validate_fields(citizens=citizens_data)):
            raise WrongParams

        citizens_relatives = {}
        for citizen_data in citizens_data:
            citizens_relatives[citizen_data['citizen_id']] = citizen_data['relatives']

        if len(citizens_relatives) != len(citizens_data):
            raise DuplicateCitizenId

        for citizen_id in citizens_relatives:
            try:
                if not all(
                        citizen_id in citizens_relatives[citizen_relative_id]
                        for citizen_relative_id in citizens_relatives[citizen_id]
                ):
                    raise WrongRelativeData
            except KeyError:
                raise WrongRelativeData
