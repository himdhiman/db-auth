# Generated by Django 3.2.6 on 2022-02-01 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0012_alter_customuser_profile_pic"),
    ]

    operations = [
        migrations.AddField(
            model_name="staticdata",
            name="users_count",
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name="accountverification",
            name="verification_code",
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name="passwordchange",
            name="pass_slug",
            field=models.CharField(max_length=20),
        ),
    ]
