# Generated by Django 3.1.4 on 2021-01-19 11:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0014_auto_20210119_1434'),
    ]

    operations = [
        migrations.RenameField('Project', 'author', 'owner')
    ]
