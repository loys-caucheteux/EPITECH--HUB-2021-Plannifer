# Generated by Django 3.1.7 on 2021-04-19 10:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('planning', '0014_auto_20210411_1144'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_premium',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='home',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]