from django.test import TestCase

from escaperoom.models import Measurement, Variable, VariableType


class MeasurementModelTest(TestCase):
    fixtures = ['types']

    @classmethod
    def setUpTestData(cls):
        from datetime import datetime

        # Variable type with test values and expected converted values
        cls.var_types = {'str': ('hello', 'hello'), 'int': ('4', 4),
                         'float': ('5.230', 5.23), 'bool': ('1', True),
                         'toggle': ('51', True)}
        for var_type, values in cls.var_types.items():
            var = Variable.objects.create(
                name=var_type, type=VariableType.objects.get(name=var_type)
            )
            ts = datetime(2021, 1, 1, 0, 0, 0)
            Measurement.objects.create(
                timestamp=ts, variable=var, value=values[0]
            )

    def test_value_convertion(self):
        for var_type, values in self.var_types.items():
            measurement = Measurement.objects.get(variable__name=var_type)
            self.assertEqual(measurement.converted_value, values[1])
