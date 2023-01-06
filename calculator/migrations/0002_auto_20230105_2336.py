# -*- coding: UTF-8 -*-

# Generated by Django 4.1.5 on 2023-01-05 23:36

from django.db import migrations

    # name = models.CharField(max_length=31)
    # cost = models.IntegerField()

    # divident = models.IntegerField()
    # value_up = models.IntegerField()
    # value_down = models.IntegerField()

    # profit_3up = models.IntegerField()
    # profit_2up = models.IntegerField()
    # profit_1up = models.IntegerField()
    # profit_0 = models.IntegerField()
    # profit_1down = models.IntegerField()
    # profit_2down = models.IntegerField()
    # profit_3down = models.IntegerField()

data = [
    {'name': 'Obligacje', 'cost': 2000, 'value_up': 2000, 'divident': 0,
        'value_down': 2000, 'profit_up': 500, 'profit_0': 500, 'profit_down': 500},
    {'name': 'Fundusz', 'cost': 5000, 'value_up': 5000, 'divident': 0,
        'value_down': 5000, 'profit_up': 1000, 'profit_0': 1000, 'profit_down': -1000},
    {'name': 'Pik', 'cost': 3000, 'value_up': 2500},
    {'name': 'B & B', 'cost': 4000, 'value_up': 3300},
    {'name': 'Hermes', 'cost': 5000, 'value_up': 4200},
    {'name': 'Good Food', 'cost': 6000, 'value_up': 5000},
    {'name': 'InterLink', 'cost': 7000, 'value_up': 5800},
    {'name': 'Home 4U', 'cost': 8000, 'value_up': 6600},
    {'name': 'Server', 'cost': 9000, 'value_up': 7500},
    {'name': 'Egida', 'cost': 10000, 'value_up': 8300},
    {'name': 'Batory', 'cost': 11000, 'value_up': 9200},
    {'name': 'Car-Cartel', 'cost': 12000, 'value_up': 10000},
    {'name': 'Kowalski S.A.', 'cost': 14000, 'value_up': 11600},
    {'name': 'Nord Bank', 'cost': 16000, 'value_up': 13300},
    {'name': 'Euro Space', 'cost': 18000, 'value_up': 15000},
    {'name': 'East Oil', 'cost':20000, 'value_up': 16600},
]

def calculate_to_save(single_data):
    result = {}
    basic_value = single_data['cost']

    result['name'] = single_data['name']
    result['cost'] = basic_value
    result['divident'] = basic_value//5
    result['value_up'] = single_data['value_up']
    result['value_down'] = basic_value//2
    result['profit_3up'] = basic_value//2
    result['profit_2up'] = basic_value//4
    result['profit_1up'] = basic_value//8
    result['profit_0'] = 0
    result['profit_1down'] = -basic_value//8
    result['profit_2down'] = -basic_value//4
    result['profit_3down'] = -basic_value//2

    if 'divident' in single_data:
        result['divident'] = single_data['divident']
    if 'value_down' in single_data:
        result['value_down'] = single_data['value_down']
    if 'profit_up' in single_data:
        result['profit_1up'] = single_data['profit_up']
        result['profit_2up'] = single_data['profit_up']
        result['profit_3up'] = single_data['profit_up']
    if 'profit_0' in single_data:
        result['profit_0'] = single_data['profit_0']
    if 'profit_down' in single_data:
        result['profit_1down'] = single_data['profit_down']
        result['profit_2down'] = single_data['profit_down']
        result['profit_3down'] = single_data['profit_down']

    return result

def forward_migration(apps, schema_editor):
    Share = apps.get_model('calculator', 'Share')
    for el in data:
        data_to_save = calculate_to_save(el)

        share = Share()

        keys = data_to_save.keys()
        for key in keys:
            share.__setattr__(key, data_to_save[key])
        share.save()

    return


def reverse_migration(apps, schema_editor):
    Share = apps.get_model('calculator', 'Share')
    for s in Share.objects.all():
        s.delete()
    return


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0001_initial'),
    ]


    operations = [
        migrations.RunPython(forward_migration, reverse_migration),
    ]