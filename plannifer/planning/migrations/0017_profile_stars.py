# Generated by Django 3.1.7 on 2021-04-21 21:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0016_task_creator'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='stars',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]