from django.db import migrations


def add_operators_types(apps, schema_editor):
    OperatorType = apps.get_model('escaperoom', 'OperatorType')
    OperatorType.objects.bulk_create([
        OperatorType(id=1, name='equal'),
        OperatorType(id=2, name='not equal'),
        OperatorType(id=3, name='greater or equal'),
        OperatorType(id=4, name='lower or equal'),
        OperatorType(id=5, name='greater'),
        OperatorType(id=6, name='lower'),
        OperatorType(id=7, name='add'),
        OperatorType(id=8, name='substract'),
        OperatorType(id=9, name='multiply'),
        OperatorType(id=10, name='divide'),
    ])


def add_variables_types(apps, schema_editor):
    VariableType = apps.get_model('escaperoom', 'VariableType')
    VariableType.objects.bulk_create([
        VariableType(id=1, name='str'),
        VariableType(id=2, name='int'),
        VariableType(id=3, name='float'),
        VariableType(id=4, name='bool'),
        VariableType(id=5, name='toggle'),
    ])


class Migration(migrations.Migration):

    dependencies = [
        ('escaperoom', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_operators_types),
        migrations.RunPython(add_variables_types),
    ]
