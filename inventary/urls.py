from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    path('', views.home, name='home'),
    #404
    path('404/', views.error404, name='404'),
    #Sessions Urls
    path('logout/', views.signout, name='signout'),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    #App Urls
    path('inventary/', views.inventary, name='inventary'),
    path('entry/', views.entry, name='entry'),
    path('sell/<int:id>', views.sell, name='sell'),
    path('junk/', views.junk, name='junk'),
    path('cars/delete/<int:id>', views.delete, name='delete'),
    path('cars/to_junk/<int:id>', views.to_junk, name='to_junk'),
    path('cars/scratched/<int:id>', views.scratched, name='scratched'),
    #JSON Urls
    path('models/', views.models, name='models'),
    path('parts/', views.parts_sell, name='parts_sell'),
    path('charts/', views.chart_prueba, name='charts'),
    path('profile/', views.profile, name='profile'),
    path('user_settings/', views.user_settings, name='user_settings'),
    path('inventary/cars', views.inventary_cars, name='cars'),
    path('inventary/pendings', views.inventary_pendings, name='pendings'),
    path('inventary/junked', views.inventary_junked, name='junked'),
    path('inventary/parts', views.inventary_parts, name='parts'),
    path('inventary/cars-sold', views.inventary_cars_sold, name='cars_sold'),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

