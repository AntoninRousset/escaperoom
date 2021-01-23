from datetime import datetime, timedelta, timezone
from django.test import TestCase

from ..models import State, Variable

TIMEZONE = timezone.utc


class FsmTest(TestCase):
    fixtures = ['statetest']

    def test_states(self):
        states = {
            'a': State.objects.get(name='a'),
            'b': State.objects.get(name='b'),
            'a.a': State.objects.get(name='a.a'),
            'a.b': State.objects.get(name='a.b'),
        }

        timestamp = datetime(2019, 11, 5, 12, 0, 0, tzinfo=TIMEZONE)
        at = timestamp + timedelta(seconds=0)
        self.assertEqual(states['a'].is_active(at=at), False)
        self.assertEqual(states['a.a'].is_active(at=at), False)
        self.assertEqual(states['a.b'].is_active(at=at), False)
        self.assertEqual(states['b'].is_active(at=at), False)

        at = timestamp + timedelta(seconds=1)
        self.assertEqual(states['a'].is_active(at=at), True)
        self.assertEqual(states['a.a'].is_active(at=at), True)
        self.assertEqual(states['a.b'].is_active(at=at), False)
        self.assertEqual(states['b'].is_active(at=at), False)

        at = timestamp + timedelta(seconds=2)
        self.assertEqual(states['a'].is_active(at=at), True)
        self.assertEqual(states['a.a'].is_active(at=at), False)
        self.assertEqual(states['a.b'].is_active(at=at), True)
        self.assertEqual(states['b'].is_active(at=at), False)

        at = timestamp + timedelta(seconds=3)
        self.assertEqual(states['a'].is_active(at=at), False)
        self.assertEqual(states['a.a'].is_active(at=at), False)
        self.assertEqual(states['a.b'].is_active(at=at), False)
        self.assertEqual(states['b'].is_active(at=at), True)


class VariableTest(TestCase):
    fixtures = ['variabletest']

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
        timestamp = datetime(2019, 11, 5, 12, 0, 0, tzinfo=TIMEZONE)

        at = timestamp + timedelta(seconds=1)
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

        at = timestamp + timedelta(seconds=2)
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

        at = timestamp + timedelta(seconds=6)
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

        at = timestamp + timedelta(seconds=10)
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
