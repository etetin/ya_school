from rest_framework.test import APITransactionTestCase

from ya.common.models import Citizen


class TestImportBirthdays(APITransactionTestCase):
    fixtures = [
        'citizens.json'
    ]
    
    IMPORT_ID = 1

    def test_wrong_request_method(self):
        url = '/imports/1/citizens'
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)

        response = self.client.put(url)
        self.assertEqual(response.status_code, 405)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, 405)

        response = self.client.patch(url)
        self.assertEqual(response.status_code, 405)

    def test_wrong_url(self):
        response = self.client.get('/imports/142374/citizens/birthdays')
        self.assertEqual(response.status_code, 404)

    def test_getting_data(self):
        response = self.client.get(f'/imports/{self.IMPORT_ID}/citizens/birthdays')

        expected_data = {
            'data': {
                str(num): []
                for num in range(1, 12 + 1)
            }
        }
        expected_data['data']['10'] = [{'citizen_id': 1, 'count': 1}]
        expected_data['data']['11'] = [
            {'citizen_id': 1, 'count': 1},
            {'citizen_id': 2, 'count': 1},
            {'citizen_id': 3, 'count': 1},
            {'citizen_id': 4, 'count': 1},
        ]
        expected_data['data']['12'] = [{'citizen_id': 1, 'count': 2}]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(expected_data, response.data)




