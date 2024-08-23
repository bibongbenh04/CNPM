from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
	path('', views.index, name = 'index'),
	path('login', views.login, name = 'login'),
	path('music/<str:pk>', views.music, name = 'music'),
	path('signup', views.signup, name = 'signup'),
    path('spotify-token/', views.spotify_token_view, name='spotify-token'),
	path('logout', views.logout, name = 'logout'),
	path('changepass', views.change_password, name = 'changepass'),
    # path('product/<slug:url>', views.product),
    path('search/', views.search, name = 'search'),
    path('profile/<str:pk>', views.profile, name = 'profile'),
    path('liked_song/<str:pk>', views.liked, name = 'liked_song'),
    path('history/<str:pk>', views.history, name = 'history'),
    path('liked_song_process/<str:pk>', views.liked_song_process, name = 'liked_song_process'),
    path('create_playlist', views.create_playlist, name = 'create_playlist'),
    path('playlist/<str:pk>', views.playlist, name = 'playlist'),
    path('search-song/', views.search_song, name = 'search_song'),
    path('add_song/<str:pk>', views.add_song, name = 'add_song'),
    path('remove_song/<str:pk>', views.remove_song, name = 'remove_song'),
    path('edit_playlist/<str:pk>', views.edit_playlist, name = 'edit_playlist'),
]+static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)