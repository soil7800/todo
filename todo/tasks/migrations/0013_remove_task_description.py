# Generated by Django 3.1.4 on 2021-01-13 12:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0012_auto_20210113_1452'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='description',
        ),
    ]