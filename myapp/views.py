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



def music(request, url):
	context = getAudioByURI(url)
	return render(request, 'music.html', context)

def getAudioByURI(uri):
	url = "https://spotify23.p.rapidapi.com/tracks/"
	querystring = {"ids":uri}

	headers = {
		"x-rapidapi-key": "097f271c26msh6c375594a059fe7p12cc04jsn241c6c1858fa",
		"x-rapidapi-host": "spotify23.p.rapidapi.com"
	}

	response = requests.get(url, headers=headers, params=querystring)

	track = response.json()["tracks"][0]
	name_track = track["name"]
	preview_url = track["preview_url"]
	artist = track["artists"][0]["name"]
	image = track["album"]["images"][0]["url"]
	return {
		'name_track':name_track,
		'preview_url':preview_url,
		'artists': artist,
		'image': image,
	}
	
def search(request):
	if request.method == 'POST':
		query = request.POST['search_query']

		url = "https://spotify23.p.rapidapi.com/search/"

		querystring = {"q":query,"type":"tracks","offset":"0","limit":"10","numberOfTopResults":"5"}

		headers = {
			"x-rapidapi-key": "097f271c26msh6c375594a059fe7p12cc04jsn241c6c1858fa",
			"x-rapidapi-host": "spotify23.p.rapidapi.com"
		}

		response = requests.get(url, headers=headers, params=querystring)

		tracks = response.json()["tracks"]["items"]
		data = []
		for track in tracks:
			track_name = track["data"]["name"]
			track_coverArt = track["data"]["albumOfTrack"]["coverArt"]["sources"][0]["url"]
			track_duration = track["data"]["duration"]["totalMilliseconds"]
			track_uri = track["data"]["uri"]
			track_artist = track["data"]["artists"]["items"][0]["profile"]["name"]
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
			'totalCount': response.json()["tracks"]["totalCount"]
		}

		return render(request, 'search.html', context)
	else:
		return render(request, 'search.html')

# Create your views here.
def index(request):
	heads = Header.objects.filter(is_active = True)
	posts = Post.objects.all()[:5]
	cats = Category.objects.filter(is_active = True)

	data = {
		'heads': heads,
		'posts' : posts,
		'cats': cats
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

		if user is not None:
			auth.login(request, user)
			return redirect('/')
		else:
			storage = django_messages.get_messages(request)
			storage.used = True
			django_messages.info(request, 'Thông tin đăng nhập chưa chính xác !')
			return redirect('login')
	else:
		return render(request, 'themes/login.html')

def logout(request):
	auth.logout(request)
	return redirect('/')

def signup(request):
	if request.method == 'POST':
		username = request.POST['username']
		email = request.POST['email']
		password = request.POST['password']
		password2 = request.POST['confirm_password']

		if password == password2:
			if User.objects.filter(email=email).exists():
				django_messages.info(request, 'Email Đã Được Sử Dụng')
				return redirect('signup')
			elif User.objects.filter(username=username).exists():
				django_messages.info(request, 'Username Đã Được Sử Dụng')
				return redirect('signup')
			else:
				user = User.objects.create_user(username=username, email=email, password=password)
				user.save()
				return redirect('login')
		else:
			django_messages.info(request, 'Mật Khẩu Không Trùng')
			return redirect('signup')
	else:
		return render(request, 'themes/signup.html')
	
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
