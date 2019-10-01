import json


class Citizen:
    GENDERS = ['male', 'female']

    @staticmethod
    def convert_for_insert(data):
        return {
            citizen_data['citizen_id']: json.dumps({
                'town': citizen_data['town'],
                'street': citizen_data['street'],
                'building': citizen_data['building'],
                'apartment': citizen_data['apartment'],
                'name': citizen_data['name'],
                'birth_date': citizen_data['birth_date'],
                'gender': citizen_data['gender'],
                'relatives': citizen_data['relatives'],
            })
            for citizen_data in data
        }

    @staticmethod
    def convert_to_object(data):
        return [
            {'citizen_id': citizen_id, **json.loads(data[citizen_id])}
            for citizen_id in data
        ]
