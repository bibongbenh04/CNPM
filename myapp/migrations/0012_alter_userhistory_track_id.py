# Generated by Django 5.1 on 2024-08-28 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0011_alter_user_playlist_playlist_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userhistory',
            name='track_id',
            field=models.CharField(max_length=255),
        ),
    ]
