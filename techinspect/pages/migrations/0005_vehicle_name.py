# Generated by Django 3.1.2 on 2020-11-25 02:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0004_auto_20201116_1859'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='name',
            field=models.CharField(max_length=25, null=True),
        ),
    ]
