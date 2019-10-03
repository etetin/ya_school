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
        'relatives': [2]
    }
    CITIZEN2 = {
        'citizen_id': 2,
        'town': 'Москва',
        'street': 'Льва Толстого',
        'building': '16к7стр5',
        'apartment': 2,
        'name': 'Иванов Иван Иванович',
        'birth_date': '01.02.2000',
        'gender': 'male',
        'relatives': [1]
    }
    CITIZEN3 = {
        'citizen_id': 3,
        'town': 'Москва',
        'street': 'Льва Толстого',
        'building': '16к7стр5',
        'apartment': 2,
        'name': 'Иванов Иван Иванович',
        'birth_date': '01.02.2000',
        'gender': 'male',
        'relatives': []
    }

    REQUEST_URL = '/imports'

    def test_wrong_request_method(self):
        response = self.client.get(self.REQUEST_URL)
        self.assertEqual(response.status_code, 405)

        response = self.client.put(self.REQUEST_URL)
        self.assertEqual(response.status_code, 405)

        response = self.client.delete(self.REQUEST_URL)
        self.assertEqual(response.status_code, 405)

        response = self.client.patch(self.REQUEST_URL)
        self.assertEqual(response.status_code, 405)

    def test_wrong_param_citizen(self):
        for value in ['1', None]:
            citizen = self.CITIZEN.copy()
            citizen['citizen_id'] = value
            response = self.client.post(self.REQUEST_URL, {'citizens': [citizen]})

            self.assertEqual(response.status_code, 400)

    def test_wrong_param_town(self):
        for value in [2, None]:
            citizen = self.CITIZEN.copy()
            citizen['town'] = value
            response = self.client.post(self.REQUEST_URL, {'citizens': [citizen]})

            self.assertEqual(response.status_code, 400)

    def test_wrong_param_street(self):
        for value in [2, None]:
            citizen = self.CITIZEN.copy()
            citizen['street'] = value
            response = self.client.post(self.REQUEST_URL, {'citizens': [citizen]})

            self.assertEqual(response.status_code, 400)

    def test_wrong_param_building(self):
        for value in [2, None]:
            citizen = self.CITIZEN.copy()
            citizen['building'] = value
            response = self.client.post(self.REQUEST_URL, {'citizens': [citizen]})

            self.assertEqual(response.status_code, 400)

    def test_wrong_param_apartment(self):
        for value in ['1', None]:
            citizen = self.CITIZEN.copy()
            citizen['apartment'] = value
            response = self.client.post(self.REQUEST_URL, {'citizens': [citizen]})

            self.assertEqual(response.status_code, 400)

    def test_wrong_param_name(self):
        for value in [2, None]:
            citizen = self.CITIZEN.copy()
            citizen['name'] = value
            response = self.client.post(self.REQUEST_URL, {'citizens': [citizen]})

            self.assertEqual(response.status_code, 400)

    def test_wrong_param_birth_date(self):
        for value in [2, '123', '2001.02.03', '42.02.2012', '2.2.2012', None]:
            citizen = self.CITIZEN.copy()
            citizen['birth_date'] = value
            response = self.client.post(self.REQUEST_URL, {'citizens': [citizen]})

            self.assertEqual(response.status_code, 400)

    def test_wrong_param_gender(self):
        for value in [2, 'man', None]:
            citizen = self.CITIZEN.copy()
            citizen['gender'] = value
            response = self.client.post(self.REQUEST_URL, {'citizens': [citizen]})

            self.assertEqual(response.status_code, 400)

    def test_wrong_param_relatives_v1(self):
        values = [
            2, ['1'], 'dsa', None,  # Wrong type of values
            [80],  # non existed citizen_id
            [3],  # wrong cause citizen with id=3 not exist in relatives citizen with id=1
        ]
        for value in values:
            citizen = self.CITIZEN.copy()
            citizen['relatives'] = value
            response = self.client.post(self.REQUEST_URL, {'citizens': [citizen, self.CITIZEN2, self.CITIZEN3]})

            self.assertEqual(response.status_code, 400)

    def test_wrong_param_relatives_v2(self):
        for value in [2, ['1'], [2], 'dsa', None]:
            citizen = self.CITIZEN.copy()
            citizen['relatives'] = value
            response = self.client.post(self.REQUEST_URL, {'citizens': [citizen]})

            self.assertEqual(response.status_code, 400)

    def test_duplicate_citizen_id(self):
        citizens = [
            {
                'citizen_id': 1,
                'town': 'Москва',
                'street': 'Льва Толстого',
                'building': '16к7стр5',
                'apartment': 2,
                'name': 'Иванов Иван Иванович',
                'birth_date': '01.02.2000',
                'gender': 'male',
                'relatives': []
            },
            {
                'citizen_id': 1,
                'town': 'Москва',
                'street': 'Льва Толстого',
                'building': '16к7стр5',
                'apartment': 2,
                'name': 'Иванов Иван Иванович',
                'birth_date': '01.02.2000',
                'gender': 'male',
                'relatives': []
            }
        ]

        response = self.client.post(self.REQUEST_URL, {'citizens': citizens})
        self.assertEqual(response.status_code, 400)

    def test_valid_params(self):
        response = self.client.post(self.REQUEST_URL, {'citizens': [self.CITIZEN, self.CITIZEN2, self.CITIZEN3]})

        self.assertEqual(response.status_code, 201)

    def test_big_import(self):
        data = []

        for i in range(1, 10001 + 1):
            data.append({
                "citizen_id": i,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 2,
                "name": "Иванов Иван Иванович",
                "birth_date": "01.02.2000",
                "gender": "male",
                # create relatives with 2 previous and 2 next citizens
                "relatives": list(range(max(1, i - 2), min(i + 2, 10001) + 1))
            })

        response = self.client.post(self.REQUEST_URL, {"citizens": data})
        # f = open("demofile2.txt", "w")
        # f.write(str({"citizens": data}))
        # f.close()

        self.assertEqual(response.status_code, 201)