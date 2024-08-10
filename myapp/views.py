from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from .models import Feature, quizQuestion, Post, Category, categoryQuiz, Science, Header, Portfolio, Store, Comment, Community, ProductImage
from django.core.serializers import serialize
from django.utils.translation import gettext as _
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.contenttypes.models import ContentType
import math
import requests
import base64
import json

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

def music(request, url):
	context = getAudioByURI(url)
	return render(request, 'music.html', context)

def getAudioByURI(id):
	url = "https://api.spotify.com/v1/tracks/"
	headers = getAuthHeader()
	
	querystring = {"id"}
	query_url = url + id

	response = requests.get(query_url, headers=headers)

	if response.status_code != 200:
		print(response.status_code)
		return None
	else:
		track = response.json()
		name_track = track["name"]
		preview_url = track["preview_url"]
		artist = track["artists"][0]["name"]
		image = track["album"]["images"][0]["url"]
		uri = track["uri"]
		duration = track["duration_ms"]
		return {
			'name_track':name_track,
			'preview_url':preview_url,
			'artists': artist,
			'image': image,
			'uri': uri,
			'id': id,
			'duration': f"{int(duration)//60000:02}" + ":" + f"{math.ceil((float(duration)%60000)/1000):02}"
		}
	
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

		tracks = response.json()["tracks"]["items"]
		data = []
		for track in tracks:
			track_name = track["name"]
			track_coverArt = track["album"]["images"][0]["url"] if len(track["album"]["images"]) > 0 else None
			track_duration = track["duration_ms"]
			track_uri = track["uri"]
			track_artist = track["artists"][0]["name"]
			data.append({
				'track_name': track_name,
				'track_coverArt': track_coverArt,
				'track_duration': float(track_duration)//60000,
				'track_uri': track_uri[14:],
				'track_artist': track_artist
			})
		print(data)
		context = {  # Giả sử kết quả tìm kiếm của bạn
			'data': data,
			'query': query,
			'response':response.json(),
			'totalCount': response.json()["tracks"]["total"]
		}

		return render(request, 'search.html', context)
	else:
		return render(request, 'search.html')

# Create your views here.
def index(request):
	artist_info = top_artists()
	if artist_info is None:
		django_messages.info(request, 'Không thể lấy thông tin nghệ sĩ !')
	else:
		data = {
			'artist_info': artist_info,
		}
	return render(request, 'index.html', data)



def load_more_sciences(request):
    offset = int(request.GET.get('offset', 0))
    posts = Science.objects.all()[offset:offset+5]  # Lấy 5 bài viết tiếp theo
    return render(request, 'AdminCus/posts.html', {'posts': posts})


def generate_string(n):
    if n <= 0:
        return ""
    else:
        return ''.join(str(i) for i in range(1, n + 1))


def post(request, url):
    post = get_object_or_404(Post, url=url)
    content_type = ContentType.objects.get_for_model(Post)
    get_all_comments = Comment.objects.filter(content_type=content_type, object_id=post.pk)
    number_of_comments = get_all_comments.count()

    if request.method == 'POST':
        name = request.POST['name']
        body = request.POST['body']
        new_comment = Comment(name=name, body=body, content_type=content_type, object_id=post.pk)  # Corrected variable name
        new_comment.save()
        django_messages.success(request, 'Bình Luận Của Bạn Đã Được Thêm Vào !')
        return redirect('blog', url=url)
    
    cats = Category.objects.filter(is_active=True)
    return render(request, 'AdminCus/tpost.html', {'post': post, 'cats': cats, 'comments': get_all_comments, 'number_of_comments': number_of_comments})


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
