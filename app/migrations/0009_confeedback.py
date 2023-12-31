# Generated by Django 4.2.6 on 2023-10-24 07:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_conversation_remove_messages_user_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feedback', models.FloatField()),
                ('description', models.CharField(max_length=1000)),
                ('con_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.conversation')),
            ],
        ),
    ]
