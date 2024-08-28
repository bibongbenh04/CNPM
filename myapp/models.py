from django.db import models
from django.contrib.auth import get_user_model
import random
import string

User = get_user_model()

def generate_user_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id = models.CharField(max_length=8, default=generate_user_id, primary_key=True, unique=True)
    is_active = models.BooleanField(default=True)
    avatar = models.ImageField(upload_to='user/', default='user/default_avatar.jpg')
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_user_id()
        super(CustomUser, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.username

class MusicDataSet(models.Model):
    is_active = models.BooleanField(default=True)
    track_id = models.CharField(max_length=255, unique=True)  
    track_name = models.CharField(max_length=255)
    track_artist = models.CharField(max_length=255)
    track_popularity = models.IntegerField()
    track_album_release_date = models.DateField()  
    playlist_genre = models.IntegerField()
    danceability = models.FloatField()
    energy = models.FloatField()
    key = models.IntegerField()
    loudness = models.FloatField()
    mode = models.IntegerField()
    speechiness = models.FloatField()
    acousticness = models.FloatField()
    instrumentalness = models.FloatField()
    liveness = models.FloatField()
    valence = models.FloatField()
    tempo = models.FloatField()

    def __str__(self):
        return f"{self.track_name} by {self.track_artist}"

class UserLikedSongs(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    track_id = models.CharField(max_length=255)
    track_name = models.CharField(max_length=255)
    track_artist = models.CharField(max_length=255)
    track_popularity = models.IntegerField(default=0)
    track_duration_ms = models.IntegerField(default=0)
    track_cover_art_url = models.CharField(max_length=255)
    liked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'track_id')

    def __str__(self):
        return f"{self.user.user.username} liked {self.track_id} at {self.liked_at}"
    
class UserHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    track_id = models.CharField(max_length=255)
    track_name = models.CharField(max_length=255)
    track_artist = models.CharField(max_length=255)
    track_popularity = models.IntegerField(default=0)
    track_duration_ms = models.IntegerField(default=0)
    track_cover_art_url = models.CharField(max_length=255)
    played_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'track_id')

    def __str__(self):
        return f"{self.user.user.username} played {self.track_id} at {self.played_at}"
    
class user_playlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    playlist_name = models.CharField(max_length=255)
    playlist_id = models.CharField(max_length=255, unique=True)
    playlist_description = models.TextField()
    playlist_image = models.ImageField(upload_to='user/', default='user/default_avatar.jpg')
    playlist_tracks_ids = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.playlist_id :
            self.playlist_id  = generate_user_id()
        super(user_playlist, self).save(*args, **kwargs)

    def add_track(self, track_id):
        self.playlist_tracks_ids.extend(track_id)
        self.playlist_tracks_ids = list(set(self.playlist_tracks_ids))
        self.save()

    def __str__(self):
        return f"{self.user.user.username} created {self.playlist_name} at {self.created_at}"