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
from datetime import datetime


def getAccessToken():
	client_id = 'e6084fff3ac4446abcc6f5835c0b9845'
	client_secret = '5ab64c21c43442bfa774423eb1bb5b45'
	auth_string = f'{client_id}:{client_secret}'
	auth_bytes = auth_string.encode('utf-8')
	auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')

	url = "https://accounts.spotify.com/api/token"
	headers = {
		'Authorization': f'Basic {auth_base64}',
		'ContentType': 'application/x-www-form-urlencoded'
	}

	data = { 'grant_type': 'client_credentials' }
	result = requests.post(url, headers=headers, data=data)
	json_result = json.loads(result.content)
	access_token = json_result['access_token']
	return access_token

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
	query_url = url + "/" + track_id + "?market=VN"

	response = requests.get(query_url, headers=header)

	data = response.json()

	track_name = data["name"]
	track_coverArt = data["album"]["images"][0]["url"] if len(data["album"]["images"]) > 0 else None
	track_duration = data["duration_ms"]
	track_uri = data["uri"]
	track_artist = data["artists"][0]["name"]
	#track_preview = data["preview_url"] if "preview_url" in data else None
	track_popularity = data["popularity"]
	track_release_date = data["album"]["release_date"]
	track_artist_id = data["artists"][0]["id"]

	user = request.user
	if user.is_authenticated:
		user = CustomUser.objects.get(user=user)
		liked = UserLikedSongs.objects.filter(user=user, track_id=track_id).exists()
		SaveUserHistory(user, track_id, track_name, track_artist, track_popularity, track_duration, track_coverArt)

	print(liked)

	url_artist = "https://api.spotify.com/v1/artists"
	querystring_artist = url_artist+"/"+track_artist_id
	response_artist = requests.get(querystring_artist, headers=header)
	data_artist = response_artist.json()
	artist_image = data_artist["images"][0]["url"] if len(data_artist["images"]) > 0 else None

	track_info = {
		'track_id': track_id,
		'track_name': track_name,
		'track_coverArt': track_coverArt,
		'track_duration': track_duration,
		'track_uri': track_uri[14:],
		'track_artist': track_artist,
		'track_artist_id': track_artist_id,
		#'track_preview': track_preview
		'track_popularity': track_popularity,
		'track_album_release_date': track_release_date,
		'artist_image': artist_image,
		'liked': liked
	}

	recommend_songs_list = hybird_recommendation(track_info,num_recommendations=5)
	query_url_recommend_song = url + "?ids=" + ",".join(recommend_songs_list['track_id'].values) + "&market=VN"
	response_recommend_song = requests.get(query_url_recommend_song, headers=header)
	data_recommend_song = response_recommend_song.json()

	data_recommend_songs = []
	for song in data_recommend_song["tracks"]:
		track_name = song["name"]
		track_coverArt = song["album"]["images"][0]["url"] if len(song["album"]["images"]) > 0 else None
		track_duration = song["duration_ms"]
		track_duration_mn = f"{int(track_duration)//60000:02}" + ":" + f"{math.ceil((float(track_duration)%60000)/1000):02}"
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

	track_info['recommend_songs'] = data_recommend_songs

	return render(request, 'music.html',track_info)

def history(request, pk):
	user_id = pk
	user = get_object_or_404(CustomUser, id=user_id)
	history = UserHistory.objects.filter(user=user).order_by('-played_at')
	data = []
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
	return render(request, 'history.html', {'data': data})

def liked(request, pk):
	user_id = pk
	user = get_object_or_404(CustomUser, id=user_id)
	history = UserLikedSongs.objects.filter(user=user).order_by('-liked_at')
	data = []
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
	return render(request, 'liked_song.html', {'data': data})

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
				playlist = user_playlist(user=user, playlist_name=playlist_name, playlist_description='My playlist', playlist_image_url='/temp_stuff/playlist_image.jpg', playlist_tracks_ids=[])
				playlist.save()
			else:
				playlist_name = 'My Playlist # 1'
				playlist = user_playlist(user=user, playlist_name=playlist_name, playlist_description='My playlist', playlist_image_url='/temp_stuff/playlist_image.jpg' , playlist_tracks_ids=[])
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
			print(playlist.playlist_tracks_ids)
			print(query_track_ids)
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
			recommend_songs = hybird_recommend_for_list_of_tracks(playlist_tracks,num_recommendations=5)
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

			print(recommend_songs_list)
		data = {
			'playlist_id': playlist.playlist_id,
			'playlist_name': playlist.playlist_name,
			'playlist_description': playlist.playlist_description,
			'playlist_image_url': playlist.playlist_image_url,
			'playlist_tracks': playlist_tracks,
			'recommend_songs': recommend_songs_list
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
			'top_tracks': top_tracks
		}
	else:
		artist_info = None
		print(response.status_code)
	return render(request, 'profile.html', artist_info)

def search(request):
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
				'query': query,
				'response':response.json(),
				'totalCount': response.json()["tracks"]["total"]
			}

			return render(request, 'search.html', context)
		else:
			return render(request, 'search.html')
	else:
		return render(request, 'search.html')

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

	response = requests.get(query_url, headers=header)

	data = response.json()

	danceability = data["danceability"]
	energy = data["energy"]
	key = data["key"]
	loudness = data["loudness"]
	mode = data["mode"]
	speechiness = data["speechiness"]
	acousticness = data["acousticness"]
	instrumentalness = data["instrumentalness"]
	liveness = data["liveness"]
	valence = data["valence"]
	tempo = data["tempo"]

	track_metadata = MusicDataSet.objects.get_or_create(
		track_id=track_info['track_id'],
		track_name=track_info['track_name'],
		track_artist=track_info['track_artist'],
		track_popularity=track_info['track_popularity'],
		track_album_release_date=FormatDated(track_info['track_album_release_date']),
		playlist_genre=6, #This data is temporary not available
		danceability=danceability,
		energy=energy,
		key=key,
		loudness=loudness,
		mode=mode,
		speechiness=speechiness,
		acousticness=acousticness,
		instrumentalness=instrumentalness,
		liveness=liveness,
		valence=valence,
		tempo=tempo
	)

	if not MusicDataSet.objects.filter(track_id=track_info['track_id']).exists():
		track_metadata.save()

music_data = LoadDataSet()
def ScalerDataSet():
	scaler = MinMaxScaler()
	music_features = music_data[['danceability', 'energy', 'key',
							'loudness', 'mode', 'speechiness', 'acousticness',
							'instrumentalness', 'liveness', 'valence', 'tempo','track_popularity']].values
	music_features_scaled = scaler.fit_transform(music_features)
	return music_features_scaled

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
	weight = 1 / (time_span.days + 1)
	return weight

def hybird_recommendation(track_info,df=music_data, music_features_scaled = music_features_scaled, num_recommendations=5, alpha=0.5):
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

	# Calculate the weighted popularity scores for the most similar songs
	content_based_recommendations['weighted_popularity'] = content_based_recommendations['track_album_release_date'].apply(calculate_weighted_popularity)

	# Calculate the hybrid scores
	content_based_recommendations['hybrid_score'] = (alpha * content_based_recommendations['weighted_popularity']) + ((1 - alpha) * content_based_recommendations['track_popularity'])

	# Sort the hybrid scores in descending order
	hybrid_recommendations = content_based_recommendations.sort_values('hybrid_score', ascending=False)

	return hybrid_recommendations

def hybird_recommend_for_list_of_tracks(list_of_tracks, num_recommendations=5, alpha=0.5, df=music_data, music_features_scaled=music_features_scaled):
	hybrid_recommendations = []
	for track_info in list_of_tracks:
		if track_info['track_id'] not in df['track_id'].values:
			print("Track not in dataset. Adding track to dataset...")
			AddMusicDataToDB(track_info)
			df = LoadDataSet()
			df.sort_values('track_popularity', ascending=False, inplace=True)
			df.reset_index(drop=True, inplace=True)
			music_features_scaled = ScalerDataSet()
		
		hybrid_recommendations.append(hybird_recommendation(track_info, df, music_features_scaled, num_recommendations, alpha))

	combined_recommendations = pd.concat(hybrid_recommendations).drop_duplicates(subset='track_id').reset_index(drop=True)
	combined_recommendations = combined_recommendations.sort_values('hybrid_score', ascending=False).head(num_recommendations)

	finale_recommendations = combined_recommendations[['track_id']]

	return finale_recommendations