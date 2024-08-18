# Generated by Django 5.1 on 2024-08-16 18:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_alter_userlikedsongs_unique_together_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('track_id', models.CharField(max_length=255, unique=True)),
                ('track_name', models.CharField(max_length=255)),
                ('track_artist', models.CharField(max_length=255)),
                ('track_popularity', models.IntegerField(default=0)),
                ('track_duration_ms', models.IntegerField(default=0)),
                ('track_cover_art_url', models.CharField(max_length=255)),
                ('played_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.customuser')),
            ],
            options={
                'unique_together': {('user', 'track_id')},
            },
        ),
        migrations.CreateModel(
            name='UserLikedSongs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('track_id', models.CharField(max_length=255, unique=True)),
                ('track_name', models.CharField(max_length=255)),
                ('track_artist', models.CharField(max_length=255)),
                ('track_popularity', models.IntegerField(default=0)),
                ('track_duration_ms', models.IntegerField(default=0)),
                ('track_cover_art_url', models.CharField(max_length=255)),
                ('liked_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.customuser')),
            ],
            options={
                'unique_together': {('user', 'track_id')},
            },
        ),
    ]