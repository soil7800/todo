# Generated by Django 3.1.4 on 2020-12-22 12:54

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='deadline',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Срок'),
        ),
    ]
