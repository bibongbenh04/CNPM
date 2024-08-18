# Generated by Django 5.1 on 2024-08-14 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_customuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='MusicDataSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('track_id', models.CharField(max_length=255, unique=True)),
                ('track_name', models.CharField(max_length=255)),
                ('track_artist', models.CharField(max_length=255)),
                ('track_popularity', models.IntegerField()),
                ('track_album_release_date', models.DateField()),
                ('playlist_genre', models.IntegerField()),
                ('danceability', models.FloatField()),
                ('energy', models.FloatField()),
                ('key', models.IntegerField()),
                ('loudness', models.FloatField()),
                ('mode', models.IntegerField()),
                ('speechiness', models.FloatField()),
                ('acousticness', models.FloatField()),
                ('instrumentalness', models.FloatField()),
                ('liveness', models.FloatField()),
                ('valence', models.FloatField()),
                ('tempo', models.FloatField()),
            ],
        ),
    ]
