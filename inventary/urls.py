from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    path('', views.home, name='home'),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('inventary/', views.inventary, name='inventary'),
    path('entry/', views.entry, name='entry'),
    path('sell/', views.sell, name='sell'),
    path('junk/', views.junk, name='junk'),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

