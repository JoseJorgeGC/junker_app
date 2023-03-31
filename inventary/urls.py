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
    path('sell/<int:id>', views.sell, name='sell'),
    path('junk/', views.junk, name='junk'),
    path('cars/delete/<int:id>', views.delete, name='delete'),
    path('cars/to_junk/<int:id>', views.to_junk, name='to_junk'),
    path('cars/scratched/<int:id>', views.scratched, name='scratched'),
    path('models/', views.models, name='models'),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

