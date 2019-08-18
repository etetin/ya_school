from copy import copy

from rest_framework.test import APITransactionTestCase

from ya.common.models import Citizen


class TestImportChange(APITransactionTestCase):
    fixtures = [
        "citizens.json",
    ]

    # wrong params
    CITIZEN_WP = {
        'town': 654,
        'street': 1,
        'building': 2,
        'apartment': 'das',
        'name': 1,
        'birth_date': '91.02.2000',
        'gender': 'gemale',
        'relatives': ['2', 12]
    }

    # partial wrong params
    CITIZEN_PWP = {
        'town': 534,
        'street': "2",
    }

    # correct params
    CITIZEN_CP = {
        'town': 'Москва-123',
        'street': 'Льва Толстого',
        'building': '16к7стр5',
        'apartment': 6,
        'name': 'Иванов Иван Иванович',
        'birth_date': '01.02.2012',
        'gender': 'male',
        'relatives': [2]
    }

    # partial correct params
    CITIZEN_PCP = {
        'town': 'old town',
        'street': "road",
        'birth_date': '07.09.1996',
    }

    # partial wrong params v2
    CITIZEN_PWP_V2 = {
        'citizen_id': 1,
        'town': 'old town',
        'street': "road",
        'birth_date': '07.09.1996',
    }

    IMPORT_ID, CITIZEN_ID = 1, 1

    INITIAL_DATA = None
    
    REQUEST_URL = f'/imports/{IMPORT_ID}/citizens/{CITIZEN_ID}'

    def setUp(self):
        self.INITIAL_DATA = Citizen.objects.get(import_id=self.IMPORT_ID, citizen_id=self.CITIZEN_ID)

    def test_wrong_request_method(self):
        response = self.client.get(self.REQUEST_URL)
        self.assertEqual(response.status_code, 405)

        response = self.client.post(self.REQUEST_URL)
        self.assertEqual(response.status_code, 405)

        response = self.client.put(self.REQUEST_URL)
        self.assertEqual(response.status_code, 405)

        response = self.client.delete(self.REQUEST_URL)
        self.assertEqual(response.status_code, 405)

    # try to update all fields by wrong params
    def test_wrong_param(self):
        # this one query is select from Citizen
        with self.assertNumQueries(1):
            response = self.client.patch(self.REQUEST_URL, self.CITIZEN_WP)
            self.assertEqual(response.status_code, 400)

        actual_data = Citizen.objects.get(import_id=self.IMPORT_ID, citizen_id=self.CITIZEN_ID)
        self.assertEqual(self.INITIAL_DATA, actual_data)

    # try to update 2 fields by wrong params
    def test_partial_wrong_params(self):
        with self.assertNumQueries(1):
            response = self.client.patch(self.REQUEST_URL, self.CITIZEN_PWP)
            self.assertEqual(response.status_code, 400)

        actual_data = Citizen.objects.get(import_id=self.IMPORT_ID, citizen_id=self.CITIZEN_ID)
        self.assertEqual(self.INITIAL_DATA, actual_data)

    # try to send without data
    def test_request_without_params(self):
        with self.assertNumQueries(0):
            response = self.client.patch(self.REQUEST_URL, {})
            self.assertEqual(response.status_code, 400)

    # try to send data only with citizen_id
    def test_request_only_with_param_citizen_id(self):
        with self.assertNumQueries(0):
            response = self.client.patch(self.REQUEST_URL, {"citizen_id": 1})
            self.assertEqual(response.status_code, 400)

    # try to send data with citizen_id
    def test_request_with_param_citizen_id(self):
        with self.assertNumQueries(0):
            response = self.client.patch(self.REQUEST_URL, self.CITIZEN_PWP_V2)
            self.assertEqual(response.status_code, 400)

    # try to update all fields
    def test_correct_params(self):
        response = self.client.patch(self.REQUEST_URL, self.CITIZEN_CP)
        self.assertEqual(response.status_code, 200)

        actual_data = response.data['data']
        for key in self.CITIZEN_CP:
            self.assertEqual(self.CITIZEN_CP[key], actual_data[key])

    # try to update 2 fields
    def test_partial_correct_params(self):
        with self.assertNumQueries(2):
            response = self.client.patch(self.REQUEST_URL, self.CITIZEN_PCP)
            self.assertEqual(response.status_code, 200)

        actual_data = response.data['data']
        for key in self.CITIZEN_PCP:
            self.assertEqual(self.CITIZEN_PCP[key], actual_data[key])


