# Generated by Django 3.0.3 on 2020-04-19 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20200418_2203'),
    ]

    operations = [
        migrations.AddField(
            model_name='requestmodel',
            name='idNum',
            field=models.IntegerField(default=0),
        ),
    ]
