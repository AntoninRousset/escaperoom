from datetime import datetime, timedelta, timezone
from django.test import TestCase

from escaperoom.models import Measurement, Variable, VariableType

TIMEZONE = timezone.utc


class ModelTest(TestCase):
    fixtures = ['types']

    @classmethod
    def setUpTestData(cls):
        cls.timestamp = datetime(2019, 11, 5, 12, 0, 0, tzinfo=TIMEZONE)

        types = {
            'str': VariableType.objects.get(name='str'),
            'int': VariableType.objects.get(name='int'),
            'float': VariableType.objects.get(name='float'),
            'bool': VariableType.objects.get(name='bool'),
            'toggle': VariableType.objects.get(name='toggle'),
        }

        variables = {
            'str': Variable(name='str', type=types['str']),
            'int': Variable(name='int', type=types['int']),
            'float': Variable(
                name='float', type=types['float'], default_value='3.1415'
            ),
            'bool': Variable(
                name='bool', type=types['bool'],
                locked_at=cls.timestamp + timedelta(seconds=7),
            ),
            'toggle': Variable(name='toggle', type=types['toggle']),
        }
        Variable.objects.bulk_create(variables.values())

        measurements = [
            Measurement(
                timestamp=cls.timestamp + timedelta(seconds=1),
                variable=Variable.objects.get(name='str'),
                value='hello'
            ),
            Measurement(
                timestamp=cls.timestamp + timedelta(seconds=2),
                variable=Variable.objects.get(name='int'),
                value='42'
            ),
            Measurement(
                timestamp=cls.timestamp + timedelta(seconds=3),
                variable=Variable.objects.get(name='float'),
                value='2.7183'
            ),
            Measurement(
                timestamp=cls.timestamp + timedelta(seconds=4),
                variable=Variable.objects.get(name='bool'),
                value='2'
            ),
            Measurement(
                timestamp=cls.timestamp + timedelta(seconds=6),
                variable=Variable.objects.get(name='toggle'),
                value='3'
            ),
            Measurement(
                timestamp=cls.timestamp + timedelta(seconds=7),
                variable=Variable.objects.get(name='toggle'),
                value='6'
            ),
            Measurement(
                timestamp=cls.timestamp + timedelta(seconds=8),
                variable=Variable.objects.get(name='bool'),
                value='0'
            ),
            Measurement(
                timestamp=cls.timestamp + timedelta(seconds=9),
                variable=Variable.objects.get(name='float'),
                value='1.6180'
            ),
            Measurement(
                timestamp=cls.timestamp + timedelta(seconds=9),
                variable=Variable.objects.get(name='int'),
                value='23'
            ),
            Measurement(
                timestamp=cls.timestamp + timedelta(seconds=10),
                variable=Variable.objects.get(name='str'),
                value='world'
            ),
        ]
        Measurement.objects.bulk_create(measurements)

    def test_variable(self):
        variables = {
            'str': Variable.objects.get(name='str'),
            'int': Variable.objects.get(name='int'),
            'float': Variable.objects.get(name='float'),
            'bool': Variable.objects.get(name='bool'),
            'toggle': Variable.objects.get(name='toggle'),
        }

        at = self.timestamp + timedelta(seconds=2)
        self.assertEqual(variables['str'].value(at=at), 'hello')
        self.assertEqual(variables['int'].value(at=at), 42)
        self.assertEqual(variables['float'].value(at=at), 3.1415)
        self.assertEqual(variables['bool'].value(at=at), None)
        self.assertEqual(variables['toggle'].value(at=at), None)

        at = self.timestamp + timedelta(seconds=6)
        self.assertEqual(variables['str'].value(at=at), 'hello')
        self.assertEqual(variables['int'].value(at=at), 42)
        self.assertEqual(variables['float'].value(at=at), 2.7183)
        self.assertEqual(variables['bool'].value(at=at), True)
        self.assertEqual(variables['toggle'].value(at=at), True)

        at = self.timestamp + timedelta(seconds=10)
        self.assertEqual(variables['str'].value(at=at), 'world')
        self.assertEqual(variables['int'].value(at=at), 23)
        self.assertEqual(variables['float'].value(at=at), 1.6180)
        self.assertEqual(variables['bool'].value(at=at), True)
        self.assertEqual(variables['toggle'].value(at=at), False)
