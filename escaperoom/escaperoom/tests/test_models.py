from datetime import datetime, timedelta, timezone
from django.test import TestCase

from escaperoom.models import (
    Measurement, Operator, OperatorType, Variable, VariableType
)

TIMEZONE = timezone.utc


class ModelTest(TestCase):
    fixtures = ['operatorstypes', 'variablestypes']

    @classmethod
    def setUpTestData(cls):
        cls.timestamp = datetime(2019, 11, 5, 12, 0, 0, tzinfo=TIMEZONE)

        variables_types = {
            'str': VariableType.objects.get(name='str'),
            'int': VariableType.objects.get(name='int'),
            'float': VariableType.objects.get(name='float'),
            'bool': VariableType.objects.get(name='bool'),
            'toggle': VariableType.objects.get(name='toggle'),
        }

        variables = {
            'str': Variable(name='str', type=variables_types['str']),
            'int': Variable(name='int', type=variables_types['int']),
            'float': Variable(
                name='float', type=variables_types['float'],
                default_value='3.1415'
            ),
            'bool': Variable(
                name='bool', type=variables_types['bool'],
                locked_at=cls.timestamp + timedelta(seconds=7),
            ),
            'toggle': Variable(name='toggle', type=variables_types['toggle']),
        }
        Variable.objects.bulk_create(variables.values())

        operators = {
            'add': Operator(
                type=OperatorType.objects.get(name='add'),
                variable_a=Variable.objects.get(name='int'),
                variable_b=Variable.objects.get(name='float')
            ),
            'substract': Operator(
                type=OperatorType.objects.get(name='substract'),
                variable_a=Variable.objects.get(name='int'),
                variable_b=Variable.objects.get(name='float')
            ),
            'multiply': Operator(
                type=OperatorType.objects.get(name='multiply'),
                variable_a=Variable.objects.get(name='int'),
                variable_b=Variable.objects.get(name='float')
            ),
            'divide': Operator(
                type=OperatorType.objects.get(name='divide'),
                variable_a=Variable.objects.get(name='int'),
                variable_b=Variable.objects.get(name='float')
            ),
        }
        for operator in operators.values():
            operator.save()

        results = {
            'addition': Variable(
                name='addition', type=variables_types['float'],
                operator=operators['add']
            ),
            'substraction': Variable(
                name='substraction', type=variables_types['float'],
                operator=operators['substract']
            ),
            'multiplication': Variable(
                name='multiplication', type=variables_types['float'],
                operator=operators['multiply']
            ),
            'division': Variable(
                name='division', type=variables_types['int'],
                operator=operators['divide']
            ),
        }
        Variable.objects.bulk_create(results.values())
        variables.update(results)

        operators['pipeline'] = Operator(
            type=OperatorType.objects.get(name='add'),
            variable_a=Variable.objects.get(name='substraction'),
            variable_b=Variable.objects.get(name='division')
        )
        operators['pipeline'].save()

        variables['pipeline'] = Variable(
            name='pipeline', type=variables_types['float'],
            operator=operators['pipeline']
        )
        variables['pipeline'].save()

        measurements = [
            Measurement(
                timestamp=cls.timestamp + timedelta(seconds=0),
                variable=Variable.objects.get(name='addition'),
                value='404'
            ),
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
            'addition': Variable.objects.get(name='addition'),
            'substraction': Variable.objects.get(name='substraction'),
            'multiplication': Variable.objects.get(name='multiplication'),
            'division': Variable.objects.get(name='division'),
            'pipeline': Variable.objects.get(name='pipeline'),
        }

        at = self.timestamp + timedelta(seconds=1)
        self.assertEqual(variables['str'].value(at=at), 'hello')
        self.assertEqual(variables['int'].value(at=at), None)
        self.assertAlmostEqual(variables['float'].value(at=at), 3.1415)
        self.assertEqual(variables['bool'].value(at=at), None)
        self.assertEqual(variables['toggle'].value(at=at), None)
        self.assertEqual(variables['addition'].value(at=at), None)
        self.assertEqual(variables['substraction'].value(at=at), None)
        self.assertEqual(variables['multiplication'].value(at=at), None)
        self.assertEqual(variables['division'].value(at=at), None)
        self.assertEqual(variables['pipeline'].value(at=at), None)

        at = self.timestamp + timedelta(seconds=2)
        self.assertEqual(variables['str'].value(at=at), 'hello')
        self.assertEqual(variables['int'].value(at=at), 42)
        self.assertAlmostEqual(variables['float'].value(at=at), 3.1415)
        self.assertEqual(variables['bool'].value(at=at), None)
        self.assertEqual(variables['toggle'].value(at=at), None)
        self.assertAlmostEqual(variables['addition'].value(at=at), 45.1415)
        self.assertAlmostEqual(variables['substraction'].value(at=at), 38.8585)
        self.assertAlmostEqual(
            variables['multiplication'].value(at=at), 131.943
        )
        self.assertAlmostEqual(variables['division'].value(at=at), 13)
        self.assertAlmostEqual(variables['pipeline'].value(at=at), 51.8585)

        at = self.timestamp + timedelta(seconds=6)
        self.assertEqual(variables['str'].value(at=at), 'hello')
        self.assertEqual(variables['int'].value(at=at), 42)
        self.assertAlmostEqual(variables['float'].value(at=at), 2.7183)
        self.assertEqual(variables['bool'].value(at=at), True)
        self.assertEqual(variables['toggle'].value(at=at), True)
        self.assertAlmostEqual(variables['addition'].value(at=at), 44.7183)
        self.assertAlmostEqual(variables['substraction'].value(at=at), 39.2817)
        self.assertAlmostEqual(
            variables['multiplication'].value(at=at), 114.1686
        )
        self.assertAlmostEqual(variables['division'].value(at=at), 15)
        self.assertAlmostEqual(variables['pipeline'].value(at=at), 54.2817)

        at = self.timestamp + timedelta(seconds=10)
        self.assertEqual(variables['str'].value(at=at), 'world')
        self.assertEqual(variables['int'].value(at=at), 23)
        self.assertAlmostEqual(variables['float'].value(at=at), 1.6180)
        self.assertEqual(variables['bool'].value(at=at), True)
        self.assertEqual(variables['toggle'].value(at=at), False)
        self.assertAlmostEqual(variables['addition'].value(at=at), 24.6180)
        self.assertAlmostEqual(variables['substraction'].value(at=at), 21.382)
        self.assertAlmostEqual(
            variables['multiplication'].value(at=at), 37.214
        )
        self.assertAlmostEqual(variables['division'].value(at=at), 14)
        self.assertAlmostEqual(variables['pipeline'].value(at=at), 35.382)
