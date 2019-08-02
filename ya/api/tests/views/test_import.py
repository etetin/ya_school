from rest_framework.test import APITransactionTestCase


class TestImport(APITransactionTestCase):
    CITIZEN = {
        'citizen_id': 1,
        'town': 'Москва',
        'street': 'Льва Толстого',
        'building': '16к7стр5',
        'apartment': 2,
        'name': 'Иванов Иван Иванович',
        'birth_date': '01.02.2000',
        'gender': 'male',
        'relatives': [2, 12]
    }

    # TODO add comparing of expected and actual data

    def test_wrong_param_citizen(self):
        for value in ['1', None]:
            self.CITIZEN['citizen_id'] = value
            response = self.client.post('/api/imports', {'citizens': [self.CITIZEN]})

            self.assertEqual(response.status_code, 400)

    def test_wrong_param_town(self):
        for value in [2, None]:
            self.CITIZEN['town'] = value
            response = self.client.post('/api/imports', {'citizens': [self.CITIZEN]})

            self.assertEqual(response.status_code, 400)

    def test_wrong_param_street(self):
        for value in [2, None]:
            self.CITIZEN['street'] = value
            response = self.client.post('/api/imports', {'citizens': [self.CITIZEN]})

            self.assertEqual(response.status_code, 400)

    def test_wrong_param_building(self):
        for value in [2, None]:
            self.CITIZEN['building'] = value
            response = self.client.post('/api/imports', {'citizens': [self.CITIZEN]})

            self.assertEqual(response.status_code, 400)

    def test_wrong_param_apartment(self):
        for value in ['1', None]:
            self.CITIZEN['apartment'] = value
            response = self.client.post('/api/imports', {'citizens': [self.CITIZEN]})

            self.assertEqual(response.status_code, 400)

    def test_wrong_param_name(self):
        for value in [2, None]:
            self.CITIZEN['name'] = value
            response = self.client.post('/api/imports', {'citizens': [self.CITIZEN]})

            self.assertEqual(response.status_code, 400)

    def test_wrong_param_birth_date(self):
        for value in [2, '123', '2001.02.03', '42.02.2012', None]:
            self.CITIZEN['birth_date'] = value
            response = self.client.post('/api/imports', {'citizens': [self.CITIZEN]})

            self.assertEqual(response.status_code, 400)

    def test_wrong_param_gender(self):
        for value in [2, 'man', None]:
            self.CITIZEN['gender'] = value
            response = self.client.post('/api/imports', {'citizens': [self.CITIZEN]})

            self.assertEqual(response.status_code, 400)

    def test_wrong_param_relatives(self):
        for value in [2, ['1'], 'dsa', None]:
            self.CITIZEN['relatives'] = value
            response = self.client.post('/api/imports', {'citizens': [self.CITIZEN]})

            self.assertEqual(response.status_code, 400)

    def test_valid_params(self):
        response = self.client.post('/api/imports', {'citizens': [self.CITIZEN]})

        self.assertEqual(response.status_code, 201)
