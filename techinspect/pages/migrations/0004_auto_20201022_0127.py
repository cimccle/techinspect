# Generated by Django 3.1.1 on 2020-10-22 01:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0003_remove_user_vin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='imageID',
        ),
        migrations.RemoveField(
            model_name='user',
            name='waiverID',
        ),
    ]