from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
	path('', views.index, name = 'index'),
	path('login', views.login, name = 'login'),
	path('music/<slug:url>', views.music, name = 'music'),
	path('signup', views.signup, name = 'signup'),
	path('logout', views.logout, name = 'logout'),
	path('changepass', views.change_password, name = 'changepass'),
    # path('product/<slug:url>', views.product),
    path('search', views.search, name = 'search'),
]+static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)