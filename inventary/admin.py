from django.contrib import admin
from .models import Cars, Brands, Models

# Register your models here.
admin.site.register(Cars)
admin.site.register(Brands)
admin.site.register(Models)