# Generated by Django 3.2.6 on 2022-01-08 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_customuser_profile_pic'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=60, unique=True, verbose_name='email')),
                ('score', models.IntegerField(blank=True, default=0, null=True)),
                ('rank', models.IntegerField(blank=True, default=0, null=True)),
                ('rating', models.IntegerField(blank=True, default=0, null=True)),
                ('hard_solved', models.IntegerField(blank=True, default=0, null=True)),
                ('medium_solved', models.IntegerField(blank=True, default=0, null=True)),
                ('easy_solved', models.IntegerField(blank=True, default=0, null=True)),
                ('submissions', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='rank',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='rating',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='score',
        ),
    ]