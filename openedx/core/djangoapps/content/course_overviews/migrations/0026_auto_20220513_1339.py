# Generated by Django 3.2.13 on 2022-05-13 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_overviews', '0025_auto_20210702_1602'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseoverview',
            name='show_consultation_form',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalcourseoverview',
            name='show_consultation_form',
            field=models.BooleanField(default=False),
        ),
    ]
