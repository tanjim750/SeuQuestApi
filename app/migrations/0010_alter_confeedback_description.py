# Generated by Django 4.2.6 on 2023-10-24 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_confeedback'),
    ]

    operations = [
        migrations.AlterField(
            model_name='confeedback',
            name='description',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]