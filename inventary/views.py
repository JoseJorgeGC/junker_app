from django.shortcuts import render
from .models import *
from .entry_functions import *
from .forms import *

# Create your views here.
def entry(request):
    validate = True
    error_messages = []
    if request.method == "GET":
        context = {'form': CarsForm(), 'errors': error_messages}
        return render(request, 'entry.html', context)
    
    form = CarsForm(request.POST, request.FILES)
    if not form.is_valid():
        error_messages.append('Complete all data')
        context = {'form': CarsForm(), 'errors': error_messages}
        return render(request, 'entry.html', context)
    
    cars = Cars.objects.all()
    for car in cars:
        if car.inventary_number == request.POST['inventary_number']:
            error_messages.append('Inventary number already exist.')
            context = {'form': CarsForm(), 'errors': error_messages}
            return render(request, 'entry.html', context) 

    title_sufix = form.files['title'].name.split('.')[-1]
    if not (str.lower(title_sufix) == 'pdf'):
        error_messages.append('Title: Unknow file type. Select a PDF file.')
        context = {'form': CarsForm(), 'errors': error_messages}
        return render(request, 'entry.html', context)   
        
    request.FILES['title'] = rename_file(form.files['title'], request.POST['inventary_number'], request.POST['entry_date'])
    print(form.files['title'].name)

    image_sufix = form.files['image'].name.split('.')[-1]
    if not (str.lower(image_sufix) == 'jpeg' or str.lower(image_sufix) == 'jpg' or str.lower(image_sufix) == 'png'):
        error_messages.append('Image: Unknow image type. Select a JPG or PNG file.')
        context = {'form': CarsForm(), 'errors': error_messages}
        return render(request, 'entry.html', context)
    
    request.FILES['image'] = rename_file(form.files['image'], request.POST['inventary_number'], request.POST['entry_date'])
    form = CarsForm(request.POST, request.FILES)
    print(request.POST['year'])
    try:
        year = int(request.POST['year'])
        if not (year <= 2023 and year >= 1940):
            print('Error if year')
            error_messages.append('Year: Enter a valid year(1959-today).')
            context = {'form': CarsForm(), 'errors': error_messages}
            return render(request, 'entry.html', context)

    except:
        print('error except')
        error_messages.append('Year: Enter a valid year(1959-today).')
        context = {'form': CarsForm(), 'errors': error_messages}
        return render(request, 'entry.html', context)

    print(title_sufix)
    form.save()
    context = {'form': CarsForm(), 'errors': error_messages}
    return render(request, 'entry.html', context)

def home(request):
    return render(request, 'index.html')

def signin(request):
    return render(request, 'signin.html')

def signup(request):
    return render(request, 'signup.html')

def inventary(request):
    context = {'cars': Cars.objects.all().order_by('-entry_date')}
    return render(request, 'inventary.html', context)

def junk(request):
    context = {'form': CarsForm() }
    return render(request, 'junk.html', context)

def sell(request):
    context = {'form': CarsForm(), 'buyerform': BuyersForm(), 'soldcarform': SoldCarsForm() }
    return render(request, 'sell.html', context) 
