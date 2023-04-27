from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    path('', views.home, name='home'),
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
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

