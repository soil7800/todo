# Generated by Django 3.1.4 on 2020-12-23 06:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_auto_20201222_1554'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='tag',
            field=models.ForeignKey(blank=True, default=0, on_delete=django.db.models.deletion.CASCADE, to='tasks.tag', verbose_name='Тег'),
            preserve_default=False,
        ),
    ]