from django import forms
from .models import Cars, Buyers, SoldCars

class CarsForm(forms.ModelForm):
    class Meta:
        model = Cars
        fields = ('brand', 'model', 'inventary_number', 'year', 'entry_date', 'condition', 'title', 'image')

class BuyersForm(forms.ModelForm):
    class Meta:
        model = Buyers
        fields = ('name', 'last_name', 'dni', 'phone_number')

class SoldCarsForm(forms.ModelForm):
    class Meta:
        model = SoldCars
        fields = ('date', 'price')