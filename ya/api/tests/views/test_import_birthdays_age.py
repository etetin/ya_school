from rest_framework.test import APITransactionTestCase

from ya.common.models import Citizen


class TestImportBirthdaysAge(APITransactionTestCase):
    fixtures = [
        'citizens.json'
    ]
    
    IMPORT_ID = 3

    def test_wrong_request_method(self):
        url = '/imports/1/citizens/birthdays'
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)

        response = self.client.put(url)
        self.assertEqual(response.status_code, 405)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, 405)

        response = self.client.patch(url)
        self.assertEqual(response.status_code, 405)

    def test_wrong_url(self):
        response = self.client.get('/imports/142374/towns/stat/percentile/age')
        self.assertEqual(response.status_code, 404)

    # not best test, but it is what it is
    def test_request(self):
        response = self.client.get(f'/imports/{self.IMPORT_ID}/towns/stat/percentile/age')
        expected_data = {
            'data': [
                {
                    'town': 'spb',
                    'p50': 61.0,
                    'p75': 86.0,
                    'p99': 114.8,
                }
            ]
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(expected_data, response.data)




