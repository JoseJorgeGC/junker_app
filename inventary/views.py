from django.shortcuts import render, redirect
from .models import *
from .entry_functions import *
from .forms import *

# Create your views here.
# cars = form.save(commit=false)
def entry(request):
    validate = True
    error_messages = []
    success_messages = []
    if request.method == "GET":
        context = {'form': CarsForm(), 'errors': error_messages}
        return render(request, 'entry.html', context)
    
    form = CarsForm(request.POST, request.FILES)
    if not form.is_valid():
        error_messages.append('Complete all data')
        context = {'form': CarsForm(), 'errors': error_messages}
        return render(request, 'entry.html', context)
    
    entry_car = form.save(commit = False)

    cars = Cars.objects.all()
    if cars:
        for car in cars:
            if car.inventary_number == entry_car.inventary_number:
                error_messages.append('Inventary number already exist.')
                context = {'form': CarsForm(), 'errors': error_messages}
                return render(request, 'entry.html', context) 

    title_sufix = entry_car.title.name.split('.')[-1]
    if not (str.lower(title_sufix) == 'pdf'):
        error_messages.append('Title: Unknow file type. Select a PDF file.')
        context = {'form': CarsForm(), 'errors': error_messages}
        return render(request, 'entry.html', context)   
        
    entry_car.title = rename_file(entry_car.title, entry_car.inventary_number, entry_car.entry_date)
    print(entry_car.title.name)

    image_sufix = entry_car.image.name.split('.')[-1]
    if not (str.lower(image_sufix) == 'jpeg' or str.lower(image_sufix) == 'jpg' or str.lower(image_sufix) == 'png'):
        error_messages.append('Image: Unknow image type. Select a JPG or PNG file.')
        context = {'form': CarsForm(), 'errors': error_messages}
        return render(request, 'entry.html', context)
    
    entry_car.image = rename_file(entry_car.image, entry_car.inventary_number, entry_car.entry_date)
    print(entry_car.year)
    try:
        year = int(entry_car.year)
        if not (year <= 2023 and year >= 1940):
            print('Error if year')
            error_messages.append('Year: Enter a valid year(1959-today).')
            context = {'form': CarsForm(), 'errors': error_messages}
            return render(request, 'entry.html', context)

    except:
        print('error except')
        error_messages.append('Year: Enter a valid year(1940-today).')
        context = {'form': CarsForm(), 'errors': error_messages}
        return render(request, 'entry.html', context)

    print(title_sufix)
    entry_car.save()
    success_messages.append(f'Car {entry_car.inventary_number} added successfully.')
    context = {'form': CarsForm(), 'errors': error_messages, 'success': success_messages}
    return render(request, 'entry.html', context)

def home(request):
    return render(request, 'index.html')

def signin(request):
    return render(request, 'signin.html')

def signup(request):
    return render(request, 'signup.html')

def inventary(request):
    context = {'cars': Cars.objects.filter(waiting = True).order_by('-entry_date')}
    return render(request, 'inventary.html', context)

def junk(request):
    context = {'form': CarsForm() }
    return render(request, 'junk.html', context)

def sell(request):
    context = {'form': CarsForm(), 'buyerform': BuyersForm(), 'soldcarform': SoldCarsForm() }
    return render(request, 'sell.html', context) 

def delete(request, id):
    car = Cars.objects.get(id = id)
    car.delete()
    messages = f'Car {car.inventary_number} deleted successfully.'
    context = {'cars': Cars.objects.filter(waiting = True).order_by('-entry_date'), 'message': messages}
    return render(request, 'inventary.html', context)

def to_junk(request, id):
    car = Cars.objects.get(id = id)
    car.waiting = False
    car.save()
    car_to_junk = JunkCars(car = car)
    car_to_junk.save()
    messages = f'Car {car.inventary_number} marked to junk successfully.'
    context = {'cars': Cars.objects.filter(waiting = True).order_by('-entry_date'), 'message': messages}
    return render(request, 'inventary.html', context)

