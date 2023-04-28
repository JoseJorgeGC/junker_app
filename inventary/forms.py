from django import forms
from .models import Cars, Buyers, SoldCars, Models
from django.contrib.auth.models import User


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password')

class CarsForm(forms.ModelForm):
    class Meta:
        model = Cars
        fields = ('brand', 'model', 'inventary_number', 'year', 'entry_date', 'condition', 'title', 'image', 'title_condition', 'vin_number', 'price')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['model'].queryset = Models.objects.none()
        
        if 'brand' in self.data:
            try:
                brand_id = int(self.data.get('brand'))
                self.fields['model'].queryset = Models.objects.filter(brand__id=brand_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['model'].queryset = self.instance.brand.model_set.order_by('name')
    
class BuyersForm(forms.ModelForm):
    class Meta:
        model = Buyers
        fields = ('name', 'last_name', 'dni', 'phone_number')

class SoldCarsForm(forms.ModelForm):
    class Meta:
        model = SoldCars
        fields = ('date', 'price')

class ShowCarsForm(forms.ModelForm):
    class Meta:
        model = Cars
        fields = ('brand', 'model', 'inventary_number', 'year', 'entry_date', 'condition', 'title', 'image')
