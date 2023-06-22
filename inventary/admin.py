from django.contrib import admin
from .models import Cars, Brands, Models, Customer

# Register your models here.
admin.site.register(Cars)
admin.site.register(Brands)
admin.site.register(Models)
admin.site.register(Customer)