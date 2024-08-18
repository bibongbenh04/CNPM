from django.core.management.base import BaseCommand
from django.db import connection
from myapp.models import MusicDataSet
import pickle
import pandas as pd

class Command(BaseCommand):
    help = 'Import data from a pickle file'

    def handle(self, *args, **kwargs):
        with open('music_recommend.pkl', 'rb') as f:
            data = pickle.load(f)
        if isinstance(data, pd.DataFrame):
            for index,row in data.iterrows():
                MusicDataSet.objects.create(
                    track_id=row['track_id'],
                    track_name=row['track_name'],
                    track_artist=row['track_artist'],
                    track_popularity=row['track_popularity'],
                    track_album_release_date=row['track_album_release_date'],
                    playlist_genre=row['playlist_genre'],
                    danceability=row['danceability'],
                    energy=row['energy'],
                    key=row['key'],
                    loudness=row['loudness'],
                    mode=row['mode'],
                    speechiness=row['speechiness'],
                    acousticness=row['acousticness'],
                    instrumentalness=row['instrumentalness'],
                    liveness=row['liveness'],
                    valence=row['valence'],
                    tempo=row['tempo']
                )
            self.stdout.write(self.style.SUCCESS('Data imported successfully'))
        else:
            self.stdout.write(self.style.ERROR('Data is not a pandas DataFrame'))


    