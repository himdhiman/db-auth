# Generated by Django 3.2.6 on 2021-10-23 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_customuser_profile_pic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='profile_pic',
            field=models.TextField(),
        ),
    ]
