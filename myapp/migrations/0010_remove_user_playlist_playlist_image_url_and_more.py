# Generated by Django 5.1 on 2024-08-22 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_user_playlist'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user_playlist',
            name='playlist_image_url',
        ),
        migrations.AddField(
            model_name='user_playlist',
            name='playlist_image',
            field=models.ImageField(default='playlist/default_playlist.jpg', upload_to='playlist/'),
        ),
    ]
