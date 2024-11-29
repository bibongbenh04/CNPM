from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.utils.translation import gettext as _
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.db import connection
from django.http import JsonResponse
from .models import CustomUser, MusicDataSet, UserLikedSongs, UserHistory, user_playlist
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse
import math
import requests
import base64
import json
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import OneHotEncoder
from datetime import datetime
from django.http import JsonResponse

def spotify_token_view(request):
    access_token = getAccessToken()
    return JsonResponse({'access_token': access_token})


def getAccessToken():
    client_id = 'e6084fff3ac4446abcc6f5835c0b9845'
    client_secret = '5ab64c21c43442bfa774423eb1bb5b45'
    auth_string = f'{client_id}:{client_secret}'
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')

    url = "https://accounts.spotify.com/api/token"
    headers = {
        'Authorization': f'Basic {auth_base64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    data = { 'grant_type': 'client_credentials' }
    try:
        result = requests.post(url, headers=headers, data=data)
        result.raise_for_status()  # Raise an exception for HTTP errors
        json_result = result.json()
        access_token = json_result.get('access_token')
        print(json_result)
        return access_token
    except requests.RequestException as e:
        print(f'Error fetching access token: {e}')
        return None


def getAuthHeader():
	access_token = getAccessToken()
	return {'Authorization': f'Bearer {access_token}'}

def SaveUserHistory(user, track_id, track_name, track_artist, track_popularity, track_duration_ms, track_cover_art_url):
	if not UserHistory.objects.filter(user=user, track_id=track_id).exists():
		UserHistory.objects.get_or_create(
			user=user,
			track_id=track_id,
			track_name=track_name,
			track_artist=track_artist,
			track_popularity=track_popularity,
			track_duration_ms=track_duration_ms,
			track_cover_art_url=track_cover_art_url,
			played_at = timezone.localtime(timezone.now())
		)
		UserHistory.objects.all().order_by('user')
	else:
		UserHistory.objects.filter(user=user, track_id=track_id).update(
			track_name=track_name,
			track_artist=track_artist,
			track_popularity=track_popularity,
			track_duration_ms=track_duration_ms,
			track_cover_art_url=track_cover_art_url,
			played_at = timezone.localtime(timezone.now())
		)

def top_artists():
	url = "https://api.spotify.com/v1/artists"
	headers = getAuthHeader()

	querystring = "?ids=5dfZ5uSmzR7VQK0udbAVpf,5HZtdKfC4xU0wvhEyYDWiY,6NF9Oa4ThQWCj6mogFSrVD,6d0dLenjy5CnR5ZMn2agiV,6zUWZmyi5MLOEynQ5wCI5f,5M3ffmRiOX9Q8Y4jNeR5wu"

	query_url = url + querystring

	response = requests.get(query_url, headers=headers)

	
	if response.status_code == 200:
		artists = response.json()["artists"]
		data = []
		for artist in artists:
			artist_name = artist["name"]
			artist_coverArt = artist["images"][0]["url"] if len(artist["images"]) > 0 else None
			artist_uri = artist["uri"]
			artist_id = artist["id"]
			data.append({
				'artist_name': artist_name,
				'artist_coverArt': artist_coverArt,
				'artist_uri': artist_uri[15:],
				'artist_id': artist_id
			})
	else:
		data = None
		print(response.status_code)

	return data

def music(request, pk):
    track_id = pk
    header = getAuthHeader()

    url = "https://api.spotify.com/v1/tracks"
    query_url = f"{url}/{track_id}?market=VN"

    response = requests.get(query_url, headers=header)
    data = response.json()

    track_name = data["name"]
    track_coverArt = data["album"]["images"][0]["url"] if len(data["album"]["images"]) > 0 else None
    track_duration = data["duration_ms"]
    track_uri = data["uri"]
    track_artist = data["artists"][0]["name"]
    track_popularity = data["popularity"]
    track_release_date = data["album"]["release_date"]
    track_artist_id = data["artists"][0]["id"]

    user = request.user
    liked = False
    if user.is_authenticated:
        user_obj = CustomUser.objects.get(user=user)
        liked = UserLikedSongs.objects.filter(user=user_obj, track_id=track_id).exists()
        SaveUserHistory(user_obj, track_id, track_name, track_artist, track_popularity, track_duration, track_coverArt)

    playlist_content = (
        user_playlist.objects.filter(user=user_obj) if user.is_authenticated and user_playlist.objects.filter(user=user_obj).exists() else None
    )

    # Fetch artist data
    url_artist = f"https://api.spotify.com/v1/artists/{track_artist_id}"
    response_artist = requests.get(url_artist, headers=header)
    data_artist = response_artist.json()
    artist_image = data_artist.get("images", [{}])[0].get("url", None)

    track_info = {
        'track_id': track_id,
        'track_name': track_name,
        'track_coverArt': track_coverArt,
        'track_duration': track_duration,
        'track_uri': track_uri[14:],
        'track_artist': track_artist,
        'track_artist_id': track_artist_id,
        'track_popularity': track_popularity,
        'track_album_release_date': track_release_date,
        'artist_image': artist_image,
        'liked': liked,
        'playlist_content': playlist_content
    }

    # Fetch recommended songs
    recommend_songs_list = hybird_recommendation(track_info, num_recommendations=5)
    query_url_recommend_song = f"{url}?ids={','.join(recommend_songs_list['track_id'].values)}&market=VN"
    response_recommend_song = requests.get(query_url_recommend_song, headers=header)

    if response_recommend_song.status_code != 200:
        print(f"Error fetching recommended songs: {response_recommend_song.status_code}")
        data_recommend_song = {"tracks": []}
    else:
        data_recommend_song = response_recommend_song.json()

    # Parse recommended songs
    data_recommend_songs = []
    for song in data_recommend_song.get("tracks", []):  # Default to empty list if "tracks" not found
        track_name = song["name"]
        track_coverArt = song["album"]["images"][0]["url"] if len(song["album"]["images"]) > 0 else None
        track_duration = song["duration_ms"]
        track_duration_mn = f"{int(track_duration) // 60000:02}:{math.ceil((float(track_duration) % 60000) / 1000):02}"
        track_uri = song["uri"]
        track_popularity = song["popularity"]
        track_artist = song["artists"][0]["name"]

        recommend_track_info = {
            'track_name': track_name,
            'track_coverArt': track_coverArt,
            'track_duration': track_duration_mn,
            'track_uri': track_uri[14:],
            'track_popularity': track_popularity,
            'track_artist': track_artist
        }

        data_recommend_songs.append(recommend_track_info)

    # Update track info with recommendations
    track_info['recommend_songs'] = data_recommend_songs

    return render(request, 'music.html', track_info)

def get_genre_seed():
	header = getAuthHeader()
	url = "https://api.spotify.com/v1/recommendations/available-genre-seeds"
	response = requests.get(url, headers=header)
	data = response.json()
	genre_seed = data['genres']
	return genre_seed

def history(request, pk):
	user_id = pk
	user = get_object_or_404(CustomUser, id=user_id)
	history = UserHistory.objects.filter(user=user).order_by('-played_at')
	data = []
	playlist_content = []

	user = request.user
	if user.is_authenticated:
		user = CustomUser.objects.get(user=user)
		print(user.avatar)
		if user_playlist.objects.filter(user=user).exists():
			playlist_content = user_playlist.objects.filter(user=user)
		else:
			playlist_content = None

	for track in history:
		track_name = track.track_name
		track_coverArt = track.track_cover_art_url
		track_duration = track.track_duration_ms
		track_uri = track.track_id
		track_artist = track.track_artist
		track_popularity = track.track_popularity
		data.append({
			'track_name': track_name,
			'track_coverArt': track_coverArt,
			'track_duration': f"{int(track_duration)//60000:02}" + ":" + f"{math.ceil((float(track_duration)%60000)/1000):02}",
			'track_uri': track_uri,
			'track_artist': track_artist,
			'track_popularity': track_popularity,
		})

	context = {
		'data': data,
		'playlist_content': playlist_content
	}
	return render(request, 'history.html', context)

def liked(request, pk):
	user_id = pk
	user = get_object_or_404(CustomUser, id=user_id)
	history = UserLikedSongs.objects.filter(user=user).order_by('-liked_at')
	data = []

	playlist_content = []

	user = request.user
	if user.is_authenticated:
		user = CustomUser.objects.get(user=user)
		print(user.avatar)
		if user_playlist.objects.filter(user=user).exists():
			playlist_content = user_playlist.objects.filter(user=user)
		else:
			playlist_content = None

	for track in history:
		track_name = track.track_name
		track_coverArt = track.track_cover_art_url
		track_duration = track.track_duration_ms
		track_uri = track.track_id
		track_artist = track.track_artist
		track_popularity = track.track_popularity
		data.append({
			'track_name': track_name,
			'track_coverArt': track_coverArt,
			'track_duration': f"{int(track_duration)//60000:02}" + ":" + f"{math.ceil((float(track_duration)%60000)/1000):02}",
			'track_uri': track_uri,
			'track_artist': track_artist,
			'track_popularity': track_popularity,
		})
	context = {
		'data': data,
		'playlist_content': playlist_content
	}
	return render(request, 'liked_song.html', context)

def liked_song_process(request, pk):
	if request.method == 'POST':
		track_id = request.POST.get('track_id')
		user = request.user
		track_name = request.POST.get('track_name')
		track_artist = request.POST.get('track_artist')
		track_popularity = request.POST.get('track_popularity')
		track_duration = request.POST.get('track_duration')
		track_coverArt = request.POST.get('track_coverArt')

		if user.is_authenticated:
			user = CustomUser.objects.get(user=user)
			if not UserLikedSongs.objects.filter(user=user, track_id=track_id).exists():
				UserLikedSongs.objects.get_or_create(user=user, track_id=track_id, track_name=track_name, track_artist=track_artist, track_popularity=track_popularity, track_duration_ms=track_duration, track_cover_art_url=track_coverArt)
				UserLikedSongs.objects.all().order_by('user')
			else:
				UserLikedSongs.objects.filter(user=user, track_id=track_id).delete()
				UserLikedSongs.objects.all().order_by('user')
		return HttpResponseRedirect(reverse('music', args=[str(pk)]))

def create_playlist(request):
	print('Create playlist')
	user = request.user
	if user.is_authenticated:
		user = CustomUser.objects.get(user=user)
		if request.method == 'POST':
			if user_playlist.objects.filter(user=user).exists():
				playlist_name = 'My Playlist # ' + str(user_playlist.objects.filter(user=user).count() + 1)
				playlist = user_playlist(user=user, playlist_name=playlist_name, playlist_description='My playlist', playlist_image='/temp_stuff/playlist_image.jpg', playlist_tracks_ids=[])
				playlist.save()
			else:
				playlist_name = 'My Playlist # 1'
				playlist = user_playlist(user=user, playlist_name=playlist_name, playlist_description='My playlist', playlist_image='/temp_stuff/playlist_image.jpg' , playlist_tracks_ids=[])
				playlist.save()
		return redirect('playlist', pk=playlist.playlist_id)
	
def playlist(request, pk):
	playlist_id = pk
	user = request.user
	header = getAuthHeader()
	url = "https://api.spotify.com/v1/tracks"
	if user.is_authenticated:
		user = CustomUser.objects.get(user=user)
		playlist = get_object_or_404(user_playlist, playlist_id=playlist_id)
		playlist_tracks = []
		if playlist.playlist_tracks_ids != None and len(playlist.playlist_tracks_ids) > 0:
			for track_id in playlist.playlist_tracks_ids:
				query_track_ids = ",".join(playlist.playlist_tracks_ids)
			query_url = url + "?market=VN&ids=" + query_track_ids
			response = requests.get(query_url, headers=header)
			data = response.json()
			track_number = 1
			for track in data["tracks"]:
				track_id = track["id"]
				track_name = track["name"]
				track_coverArt = track["album"]["images"][0]["url"] if len(track["album"]["images"]) > 0 else None
				track_duration = track["duration_ms"]
				track_uri = track["uri"]
				track_artist = track["artists"][0]["name"]
				track_popularity = track["popularity"]
				track_album_release_date = track["album"]["release_date"]
				convert_date = FormatDated(track_album_release_date)
				track_info = {
					'track_id': track_id,
					'track_name': track_name,
					'track_coverArt': track_coverArt,
					'track_duration': f"{int(track_duration)//60000:02}" + ":" + f"{math.ceil((float(track_duration)%60000)/1000):02}",
					'track_uri': track_uri[14:],
					'track_artist': track_artist,
					'track_popularity': track_popularity,
					'track_number': track_number,
					'track_album_release_date': convert_date
				}
				track_number += 1
				playlist_tracks.append(track_info)
		else:
			playlist_tracks = None
		
		recommend_songs_list = None
		
		if playlist_tracks is not None:
			
			recommend_songs = hybird_recommendation_using_scaled(playlist.playlist_tracks_ids, num_recommendations=5)
			query_recommend_songs = ",".join(recommend_songs['track_id'].values)
			query_url_recommend_songs = url + "?market=VN&ids=" + query_recommend_songs
			response_recommend_songs = requests.get(query_url_recommend_songs, headers=header)
			data_recommend_songs = response_recommend_songs.json()
			recommend_songs_list = []
			for song in data_recommend_songs["tracks"]:
				track_id = song["id"]
				track_name = song["name"]
				track_coverArt = song["album"]["images"][0]["url"] if len(song["album"]["images"]) > 0 else None
				track_duration = song["duration_ms"]
				track_duration_mn = f"{int(track_duration)//60000:02}" + ":" + f"{math.ceil((float(track_duration)%60000)/1000):02}"
				track_uri = song["uri"]
				track_popularity = song["popularity"]
				track_artist = song["artists"][0]["name"]

				recommend_track_info = {
					'track_id': track_id,
					'track_name': track_name,
					'track_coverArt': track_coverArt,
					'track_duration': track_duration_mn,
					'track_uri': track_uri[14:],
					'track_popularity': track_popularity,
					'track_artist': track_artist
				}

				recommend_songs_list.append(recommend_track_info)

		user = request.user
		if user.is_authenticated:
			user = CustomUser.objects.get(user=user)
			print(user.avatar)
			if user_playlist.objects.filter(user=user).exists():
				playlist_content = user_playlist.objects.filter(user=user)
			else:
				playlist_content = None

		data = {
			'playlist_id': playlist.playlist_id,
			'playlist_name': playlist.playlist_name,
			'playlist_description': playlist.playlist_description,
			'playlist_image': playlist.playlist_image,
			'playlist_tracks': playlist_tracks,
			'recommend_songs': recommend_songs_list,
			'playlist_content': playlist_content
		}

		return render(request, 'playlist.html', data)

def add_song(request, pk):
	playlist_id = pk
	if request.method == 'POST':
		track_id = request.POST.get('track_id')
		print(track_id)
		user = request.user
		if user.is_authenticated:
			user = CustomUser.objects.get(user=user)
			playlist = get_object_or_404(user_playlist, playlist_id=playlist_id)
			if track_id not in playlist.playlist_tracks_ids:
				playlist.playlist_tracks_ids.append(track_id)
				print(playlist.playlist_tracks_ids)
				playlist.save()
		return HttpResponseRedirect(reverse('playlist', args=[str(playlist_id)]))

def remove_song(request, pk):
	playlist_id = pk
	if request.method == 'POST':
		track_id = request.POST.get('track_id')
		user = request.user
		if user.is_authenticated:
			user = CustomUser.objects.get(user=user)
			playlist = get_object_or_404(user_playlist, playlist_id=playlist_id)
			if track_id in playlist.playlist_tracks_ids:
				playlist.playlist_tracks_ids.remove(track_id)
				playlist.save()
		return HttpResponseRedirect(reverse('playlist', args=[str(playlist_id)]))
	
def edit_playlist(request, pk):
	playlist_id = pk
	if request.method == 'POST':
		playlist_name = request.POST.get('playlist_name')
		playlist_description = request.POST.get('playlist_description')
		playlist_image_url = request.FILES.get('playlist_image')
		print(playlist_image_url)
		user = request.user
		if user.is_authenticated:
			user = CustomUser.objects.get(user=user)
			playlist = get_object_or_404(user_playlist, playlist_id=playlist_id)
			#playlist = user_playlist.objects.filter(user=user, playlist_id=playlist_id).update(playlist_name=playlist_name, playlist_description=playlist_description, playlist_image=playlist_image_url)
			playlist.playlist_name = playlist_name
			playlist.playlist_description = playlist_description
			print(playlist_image_url)
			if playlist_image_url:
				playlist.playlist_image = playlist_image_url
			playlist.save()
		return HttpResponseRedirect(reverse('playlist', args=[str(playlist_id)]))

def top_tracks():
	url = "https://api.spotify.com/v1/playlists"
	query_string = "/37i9dQZEVXbLdGSmz6xilI?market=VN"
	query_url = url + query_string
	
	headers = getAuthHeader()

	response = requests.get(query_url, headers=headers)

	if response.status_code == 200:
		tracks = response.json()["tracks"]["items"]
		data = []
		for track in tracks:
			track_name = track["track"]["name"]
			track_coverArt = track["track"]["album"]["images"][0]["url"] if len(track["track"]["album"]["images"]) > 0 else None
			track_uri = track["track"]["uri"]
			track_id = track["track"]["id"]
			data.append({
				'track_name': track_name,
				'track_coverArt': track_coverArt,
				'track_uri': track_uri[14:],
				'track_id': track_id
			})

		return data
	else:
		return None

def profile(request, pk):
	artist_id = pk

	url = "https://api.spotify.com/v1/artists"

	querystring = url+"/"+artist_id

	headers = getAuthHeader()

	response = requests.get(querystring, headers=headers)

	# Get top tracks
	querystring2 = "https://api.spotify.com/v1/artists/"+artist_id+"/top-tracks" + "?market=VN"

	response2 = requests.get(querystring2, headers=headers)

	playlist_content = []

	user = request.user
	if user.is_authenticated:
		user = CustomUser.objects.get(user=user)
		print(user.avatar)
		if user_playlist.objects.filter(user=user).exists():
			playlist_content = user_playlist.objects.filter(user=user)
		else:
			playlist_content = None

	if response.status_code == 200 and response2.status_code == 200:
		data = response.json()

		artist_name = data["name"]
		artist_monthlyListeners = data["followers"]["total"]
		artist_image = data["images"][0]["url"] if len(data["images"]) > 0 else None

		top_tracks = []

		data2 = response2.json()

		for track in data2["tracks"]:
			trackid = track["id"]
			trackname = track["name"]
			trackcoverArt = track["album"]["images"][0]["url"] if len(track["album"]["images"]) > 0 else None	
			trackuri = track["uri"]
			trackplayCount = track["popularity"]
			trackduration = track["duration_ms"]		

			track_info = {
				'trackid': trackid,
				'trackname': trackname,
				'trackcoverArt': trackcoverArt,
				'trackuri': trackuri,
				'trackplayCount': trackplayCount,
				'trackduration': f"{int(trackduration)//60000:02}" + ":" + f"{math.ceil((float(trackduration)%60000)/1000):02}",
			}	

			top_tracks.append(track_info)

		artist_info = {
			'artist_name': artist_name,
			'artist_monthlyListeners': artist_monthlyListeners,
			'artist_image': artist_image,
			'top_tracks': top_tracks,
			'playlist_content': playlist_content
		}
	else:
		artist_info = None
		print(response.status_code)
	return render(request, 'profile.html', artist_info)

def search(request):
	playlist_content = []

	user = request.user
	if user.is_authenticated:
		user = CustomUser.objects.get(user=user)
		if user_playlist.objects.filter(user=user).exists():
			playlist_content = user_playlist.objects.filter(user=user)
		else:
			playlist_content = None

	if request.method == 'POST':
		query = request.POST['search_query']

		url = "https://api.spotify.com/v1/search"

		querystring = "?q="+query+"&type=track&market=VN"
		query_url = url + querystring

		headers = getAuthHeader()

		response = requests.get(query_url, headers=headers)

		if response.status_code == 200:
			tracks = response.json()["tracks"]["items"]
			data = []
			for track in tracks:
				track_name = track["name"]
				track_coverArt = track["album"]["images"][0]["url"] if len(track["album"]["images"]) > 0 else None
				track_duration = track["duration_ms"]
				track_uri = track["uri"]
				track_artist = track["artists"][0]["name"]
				track_popularity = track["popularity"]
				data.append({
					'track_name': track_name,
					'track_coverArt': track_coverArt,
					'track_duration': f"{int(track_duration)//60000:02}" + ":" + f"{math.ceil((float(track_duration)%60000)/1000):02}",
					'track_uri': track_uri[14:],
					'track_artist': track_artist,
					'track_popularity': track_popularity
				})
			context = {  # Giả sử kết quả tìm kiếm của bạn
				'data': data,
				'playlist_content': playlist_content,
				'query': query,
				'response':response.json(),
				'totalCount': response.json()["tracks"]["total"]
			}

			return render(request, 'search.html', context)
		else:
			data = {'playlist_content': playlist_content}
			return render(request, 'search.html', data)
	else:
		data = {'playlist_content': playlist_content}
		return render(request, 'search.html', data)

def search_song(request):
	if request.method == 'POST':
		query = request.POST.get('search_query')

		url = "https://api.spotify.com/v1/search"

		querystring = "?q="+query+"&type=track&market=VN&limit=10"
		query_url = url + querystring

		headers = getAuthHeader()

		response = requests.get(query_url, headers=headers)

		if response.status_code == 200:
			tracks = response.json()["tracks"]["items"] 
			data = []
			for track in tracks:
				track_id = track["id"]
				track_name = track["name"]
				track_coverArt = track["album"]["images"][0]["url"] if len(track["album"]["images"]) > 0 else None
				track_duration = track["duration_ms"]
				track_uri = track["uri"]
				track_artist = track["artists"][0]["name"]
				track_popularity = track["popularity"]
				data.append({
					'track_id': track_id,
					'track_name': track_name,
					'track_coverArt': track_coverArt,
					'track_duration': f"{int(track_duration)//60000:02}" + ":" + f"{math.ceil((float(track_duration)%60000)/1000):02}",
					'track_uri': track_uri[14:],
					'track_artist': track_artist,
					'track_popularity': track_popularity
				})
			context = {  # Giả sử kết quả tìm kiếm của bạn
				'data': data,
				'query': query,
				'response':response.json(),
				'totalCount': response.json()["tracks"]["total"]
			}

			print(data)
			return JsonResponse(context)
		else:
			print('Không thể tìm thấy bài hát !')
			return JsonResponse({'error': 'Không thể tìm thấy bài hát !'})
	else:
		print('Không thể tìm thấy bài hát1 !')
		return JsonResponse({'error': 'Không thể tìm thấy bài hát !'})

@login_required(login_url='/login')
# Create your views here.
def index(request):
	artist_info = top_artists()
	top_tracks_info = top_tracks()

	first_top_tracks_section = None
	second_top_tracks_section = None
	third_top_tracks_section = None

	if top_tracks_info is None:
		django_messages.info(request, 'Không thể lấy thông tin bài hát !')
	else:
		first_top_tracks_section = top_tracks_info[:5]
		second_top_tracks_section = top_tracks_info[6:11]
		third_top_tracks_section = top_tracks_info[12:17]
	if artist_info is None:
		django_messages.info(request, 'Không thể lấy thông tin nghệ sĩ !')

	playlist_content = []

	user = request.user
	if user.is_authenticated:
		user = CustomUser.objects.get(user=user)
		if user_playlist.objects.filter(user=user).exists():
			playlist_content = user_playlist.objects.filter(user=user)
		else:
			playlist_content = None
	data = {
		'artist_info': artist_info,
		'first_top_tracks_section': first_top_tracks_section,
		'second_top_tracks_section': second_top_tracks_section,
		'third_top_tracks_section': third_top_tracks_section,
		'playlist_content': playlist_content
	}
	return render(request, 'index.html', data)

def login(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']

		user = auth.authenticate(username=username, password=password)

		if username == '' or password == '':
			django_messages.info(request, 'Vui lòng điền đầy đủ thông tin !')
			return redirect('login')

		if user is not None:
			auth.login(request, user)
			return redirect('/')
		else:
			storage = django_messages.get_messages(request)
			storage.used = True
			django_messages.info(request, 'Thông tin đăng nhập chưa chính xác !')
			return redirect('login')
	else:
		return render(request, 'login.html')

def logout(request):
	auth.logout(request)
	return redirect('/')

def signup(request):
	if request.method == 'POST':
		avatar = request.FILES.get('avatar')
		username = request.POST['username']
		email = request.POST['email']
		password = request.POST['password']
		password2 = request.POST['confirm_password']

		if username == '' or email == '' or password == '' or password2 == '':
			django_messages.info(request, 'Vui lòng điền đầy đủ thông tin !')
			return redirect('signup')

		if password == password2:
			if User.objects.filter(email=email).exists():
				django_messages.info(request, 'Email đã tồn tại !')
				return redirect('signup')
			elif User.objects.filter(username=username).exists():
				django_messages.info(request, 'Tên đăng nhập đã tồn tại !')
				return redirect('signup')
			else:
				user = User.objects.create_user(username=username, email=email, password=password)
				user.save()

				profile = CustomUser(user=user)
				if avatar:
					profile.avatar.save(avatar.name, avatar)
				else:
					profile.avatar = 'user/default_avatar.jpg'
				profile.save()

				user_login = auth.authenticate(username=username, password=password)
				auth.login(request, user_login)
				return redirect('/')
		else:
			print('Mật khẩu không khớp !')
			django_messages.info(request, 'Mật khẩu không khớp !')
			return redirect('signup')
	else:
		return render(request, 'signup.html')
	
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Cập nhật session để tránh đăng xuất
            django_messages.success(request, 'Mật khẩu của bạn đã được thay đổi thành công!')
            return redirect('/')
        else:
            django_messages.error(request, 'Vui lòng sửa lại các lỗi bên dưới.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'themes/changePass.html', {'form': form})

def LoadDataSet():
	query = "SELECT * FROM myapp_musicdataset"
	with connection.cursor() as cursor:
		cursor.execute(query)
		data = cursor.fetchall()

	# Get column names from the model
	columns = [desc[0] for desc in cursor.description]

	# Exclude 'id' and 'is_active' columns
	columns_to_exclude = ['id', 'is_active']

	df = pd.DataFrame(data, columns=columns)
	df = df.drop(columns=columns_to_exclude)
	return df

def FormatDated(date_str):
    try:
        if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
            return date_str 
        else:
            if len(date_str) == 4:
                return f"{date_str}-01-01"
            else:
                return f"{date_str}-01"
    except Exception as e:
        print(f"Error formatting date: {e}")
        return None

def AddMusicDataToDB(track_info):
    header = getAuthHeader()

    url = "https://api.spotify.com/v1/audio-features"
    query_url = url + "/" + track_info['track_id']

    try:
        response = requests.get(query_url, headers=header)
        response.raise_for_status()  # Kiểm tra lỗi HTTP
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Spotify API: {e}")
        return  # Dừng hàm nếu có lỗi API
    except ValueError:
        print("Error decoding JSON response")
        return

    # Gán giá trị mặc định cho tất cả các thuộc tính
    danceability = data.get("danceability", 0.5)
    energy = data.get("energy", 0.0)
    key = data.get("key", 0)
    loudness = data.get("loudness", -60.0)  # Giá trị mặc định nhỏ nhất
    mode = data.get("mode", 0)
    speechiness = data.get("speechiness", 0.0)
    acousticness = data.get("acousticness", 0.0)
    instrumentalness = data.get("instrumentalness", 0.0)
    liveness = data.get("liveness", 0.0)
    valence = data.get("valence", 0.0)
    tempo = data.get("tempo", 120.0)  # Giá trị mặc định thường dùng

    try:
        # Tạo hoặc lấy bản ghi trong cơ sở dữ liệu
        track_metadata, created = MusicDataSet.objects.get_or_create(
            track_id=track_info['track_id'],
            defaults={
                "track_name": track_info['track_name'],
                "track_artist": track_info['track_artist'],
                "track_popularity": track_info['track_popularity'],
                "track_album_release_date": FormatDated(track_info['track_album_release_date']),
                "playlist_genre": 6,  # Giá trị tạm thời
                "danceability": danceability,
                "energy": energy,
                "key": key,
                "loudness": loudness,
                "mode": mode,
                "speechiness": speechiness,
                "acousticness": acousticness,
                "instrumentalness": instrumentalness,
                "liveness": liveness,
                "valence": valence,
                "tempo": tempo,
            },
        )

        # Nếu bản ghi chưa tồn tại, lưu mới
        if created:
            track_metadata.save()

    except Exception as e:
        print(f"Error saving data to database: {e}")
	    
music_data = LoadDataSet()
def ScalerDataSet():
	scaler = MinMaxScaler()
	music_features = music_data[['danceability', 'energy', 'key',
							'loudness', 'mode', 'speechiness', 'acousticness',
							'instrumentalness', 'liveness', 'valence', 'tempo','track_popularity']].values
	music_features_scaled = scaler.fit_transform(music_features)
	return music_features_scaled

def get_Playlist_Avg_Features(playlist_id):
	playlist = user_playlist.objects.get(playlist_id=playlist_id)
	playlist_tracks = MusicDataSet.objects.filter(track_id__in=playlist.playlist_tracks_ids)
	df = pd.DataFrame(list(playlist_tracks.values()))
	playlist_avg_features = df[['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo','track_popularity']].mean()
	scaler = MinMaxScaler()
	playlist_avg_features_scaled = scaler.fit_transform(playlist_avg_features.values.reshape(1, -1))
	return playlist_avg_features_scaled

music_features_scaled = ScalerDataSet()

def content_based_recommendations(track_info, num_recommendations=5, df=music_data, music_features_scaled=music_features_scaled):
	if track_info['track_id'] not in df['track_id'].values:
		print("Track not in dataset. Adding track to dataset...")
		AddMusicDataToDB(track_info)
		df = LoadDataSet()
		df.sort_values('track_popularity', ascending=False, inplace=True)
		df.reset_index(drop=True, inplace=True)
		music_features_scaled = ScalerDataSet()	

    # Get the index of the input song in the music DataFrame
	input_song_index = df[df['track_id'] == track_info['track_id']].index[0]

    # Calculate the similarity scores based on music features (cosine similarity)
	similarity_scores = cosine_similarity([music_features_scaled[input_song_index]], music_features_scaled)

    # Get the indices of the most similar songs
	similar_song_indices = similarity_scores.argsort()[0][::-1][1:num_recommendations + 1]

    # Get the names of the most similar songs based on content-based filtering
	content_based_recommendations = df.iloc[similar_song_indices][['track_id','track_name', 'track_artist', 'playlist_genre', 'track_album_release_date', 'track_popularity']]

	return content_based_recommendations

# Function to calculate weighted popularity scores based on release date
def calculate_weighted_popularity(release_date):
	# Convert the release date to a datetime object
	release_date = pd.to_datetime(release_date)

    # Calculate the time span between release date and today's date
	time_span = datetime.now() - release_date

    # Calculate the weighted popularity score based on time span (e.g., more recent releases have higher weight)
	weight = 1 / time_span.days * 10 
	return weight

def hybird_recommendation(track_info, df=music_data, music_features_scaled=music_features_scaled, num_recommendations=5):
    if track_info['track_id'] not in df['track_id'].values:
        print("Track not in dataset. Adding track to dataset...")
        AddMusicDataToDB(track_info)
        df = LoadDataSet()
        df.sort_values('track_popularity', ascending=False, inplace=True)
        df.reset_index(drop=True, inplace=True)
        music_features_scaled = ScalerDataSet()

    # Check if the song exists in the updated DataFrame
    matching_songs = df[df['track_id'] == track_info['track_id']]
    if matching_songs.empty:
        print(f"Track ID {track_info['track_id']} not found in the dataset after updating. Returning empty recommendations.")
        return pd.DataFrame(columns=['track_id', 'track_name', 'track_artist', 'playlist_genre', 
                                     'track_album_release_date', 'track_popularity', 
                                     'weighted_popularity', 'hybrid_score'])

    # Get the index of the input song
    input_song_index = matching_songs.index[0]

    # Calculate similarity scores
    similarity_scores = cosine_similarity([music_features_scaled[input_song_index]], music_features_scaled)

    # Get indices of the most similar songs
    similar_song_indices = similarity_scores.argsort()[0][::-1][1:num_recommendations + 1]

    # Get song recommendations
    content_based_recommendations = df.iloc[similar_song_indices][
        ['track_id', 'track_name', 'track_artist', 'playlist_genre', 'track_album_release_date', 'track_popularity']]

    # Calculate hybrid scores
    content_based_recommendations['weighted_popularity'] = content_based_recommendations['track_album_release_date'].apply(
        calculate_weighted_popularity)
    content_based_recommendations['hybrid_score'] = (
        content_based_recommendations['track_popularity'] +
        content_based_recommendations['track_popularity'] * content_based_recommendations['weighted_popularity']
    )

    # Sort recommendations by hybrid score
    hybrid_recommendations = content_based_recommendations.sort_values('hybrid_score', ascending=False)

    return hybrid_recommendations


def getting_track_from_id(track_id):
	url = "https://api.spotify.com/v1/tracks"
	query_url = url + "/" + track_id + "?market=VN"

	header = getAuthHeader()
	response = requests.get(query_url, headers=header)

	data = response.json()

	track_id = data["id"]
	track_name = data["name"]
	track_artist = data["artists"][0]["name"]
	track_popularity = data["popularity"]
	track_album_release_date = data["album"]["release_date"]

	track_info = {
		'track_id': track_id,
		'track_name': track_name,
		'track_artist': track_artist,
		'track_popularity': track_popularity,
		'track_album_release_date': track_album_release_date
	}

	return track_info
	

def hybrid_recommendation_using_scaled(track_ids, df=music_data, music_features_scaled=music_features_scaled, num_recommendations=5):
    # Ensure all tracks in track_ids exist in the dataset
    for track in track_ids:
        if track not in df['track_id'].values:
            print(f"Track {track} not found in dataset. Adding...")
            track_info = getting_track_from_id(track)
            if not track_info:
                print(f"Track ID {track} could not be retrieved. Skipping this track.")
                continue
            AddMusicDataToDB(track_info)
            df = LoadDataSet()
            df.sort_values('track_popularity', ascending=False, inplace=True)
            df.reset_index(drop=True, inplace=True)
            music_features_scaled = ScalerDataSet()

    # Get indices of the provided track IDs in the dataset
    matching_indices = df[df['track_id'].isin(track_ids)].index

    # Handle case where none of the provided track IDs are found
    if matching_indices.empty:
        print("None of the provided track IDs are found in the dataset. Returning empty recommendations.")
        return pd.DataFrame(columns=['track_id', 'track_name', 'track_artist', 'playlist_genre', 
                                     'track_album_release_date', 'track_popularity', 
                                     'weighted_popularity', 'hybrid_score'])

    # Compute the average scaled features for the given tracks
    avg_scaled_features = music_features_scaled[matching_indices].mean(axis=0)

    # Calculate similarity scores
    similarity_scores = cosine_similarity([avg_scaled_features], music_features_scaled)

    # Get indices of the most similar songs
    similar_song_indices = similarity_scores.argsort()[0][::-1][1:num_recommendations + 1]

    # Get details of recommended songs
    content_based_recommendations = df.iloc[similar_song_indices][
        ['track_id', 'track_name', 'track_artist', 'playlist_genre', 'track_album_release_date', 'track_popularity']
    ]

    # Calculate weighted popularity and hybrid scores
    content_based_recommendations['weighted_popularity'] = content_based_recommendations['track_album_release_date'].apply(
        calculate_weighted_popularity)
    content_based_recommendations['hybrid_score'] = (
        content_based_recommendations['track_popularity'] +
        content_based_recommendations['track_popularity'] * content_based_recommendations['weighted_popularity']
    )

    # Sort recommendations by hybrid score
    hybrid_recommendations = content_based_recommendations.sort_values('hybrid_score', ascending=False)

    return hybrid_recommendations
