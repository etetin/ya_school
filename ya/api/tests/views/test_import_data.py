from rest_framework.test import APITransactionTestCase

from ya.common.models import Citizen


class TestImportData(APITransactionTestCase):
    fixtures = [
        'citizens.json'
    ]
    
    IMPORT_ID = 1

    def test_wrong_request_method(self):
        url = '/api/imports/1/citizens'
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)

        response = self.client.put(url)
        self.assertEqual(response.status_code, 405)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, 405)

        response = self.client.patch(url)
        self.assertEqual(response.status_code, 405)

    def test_wrong_url(self):
        response = self.client.get('/api/imports/142374/citizens')
        self.assertEqual(response.status_code, 404)

    def test_getting_data(self):
        with self.assertNumQueries(1):
            response = self.client.get(f'/api/imports/{self.IMPORT_ID}/citizens')
            self.assertEqual(response.status_code, 200)

        expected_data = []
        for citizen in Citizen.objects.filter(import_id=self.IMPORT_ID):
            expected_data.append({
                "citizen_id": citizen.citizen_id,
                "town": citizen.town,
                "street": citizen.street,
                "building": citizen.building,
                "apartment": citizen.apartment,
                "name": citizen.name,
                "birth_date": citizen.birth_date.strftime("%d.%m.%Y"),
                "gender": citizen.gender,
                "relatives": citizen.relatives,
            })

        self.assertEqual(expected_data, response.data['data'])


