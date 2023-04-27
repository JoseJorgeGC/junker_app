from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import IntegrityError
from .models import *
from .entry_functions import *
from .forms import *
import json
import datetime

# Create your views here.
# cars = form.save(commit=false)


#Sessions views
def signin(request):
    if request.method == "POST":
        messages = []
        user = authenticate(request, username = request.POST['username'], password = request.POST['password'])
        if user is None:
            print('Error usuario')
            messages.append('User or password incorrect.')
            context = {'signinform': AuthenticationForm()}            
            return render(request, 'signin.html', context)

        login(request, user)
        return redirect('/')
    context = {'signinform': AuthenticationForm()}            
    return render(request, 'signin.html', context)

@login_required
def signout(request):
    logout(request)
    return redirect('/signin/')

def signup(request):

    #POST Method
    if request.method == "POST":
        messages = []
        form = UserCreationForm(request.POST)
        if not form.is_valid():
            messages.append('Complete all data.')
            context = {'signupform': UserCreationForm(), 'messages': messages}
            return render(request, 'signup.html', context)
        
        if not request.POST['password'] == request.POST['repassword']:
            messages.append('Passwords does not match.')
            context = {'signupform': UserCreationForm(), 'messages': messages}
            return render(request, 'signup.html', context)
        
        try:
            user = User.objects.create_user(username = request.POST['username'], first_name = request.POST['first_name'], last_name = request.POST['last_name'], email = request.POST['email'], password = request.POST['password'])
            user.save()
            return redirect('/signin/')
        except IntegrityError:
            messages.append(f'Username {user.username} already exist.')
            context = {'signupform': UserCreationForm(), 'messages': messages}
            return render(request, 'signup.html', context)


    #GET Method
    context = {'signupform': UserCreationForm()}
    return render(request, 'signup.html', context)


#Views
@login_required
def home(request):
    junkcar_counter = JunkCars.objects.filter(waiting = True).count()
    context = {'junkcar_counter': junkcar_counter,'junkcars': JunkCars.objects.filter(waiting = True),'cars': Cars.objects.filter(waiting = True).order_by('-entry_date')}
    return render(request, 'index.html', context)

@login_required
def inventary(request):
    junkcar_counter = JunkCars.objects.filter(waiting = True).count()
    context = {'junkcar_counter': junkcar_counter,'junkcars': JunkCars.objects.filter(waiting = True),'cars': Cars.objects.filter(waiting = True).order_by('-entry_date')}
    return render(request, 'inventary.html', context)


@login_required
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

@login_required
def junk(request):
    context = {'form': CarsForm() }
    return render(request, 'junk.html', context)

#SQL Operations
@login_required
def sell(request, id):
    car = Cars.objects.get(id=id)
    if request.method == "POST":
        buyer = Buyers(name = str(request.POST['name']), last_name = request.POST['last_name'], dni = request.POST['dni'], phone_number = request.POST['phone_number'] )
        sold_car = SoldCars(car = car, buyer = buyer, price = request.POST['price'], date = request.POST['date'])
        print(sold_car)
        print(buyer)
        car.waiting = False
        car.save()
        try:
            junk = JunkCars.objects.get(car = car)
            junk.waiting = False
            junk.save()
        except:
            pass

        return redirect('/inventary/')

    context = {'form': ShowCarsForm(instance=car), 'buyerform': BuyersForm(), 'soldcarform': SoldCarsForm(), 'car': car }
    return render(request, 'sell.html', context) 

@login_required
def delete(request, id):
    car = Cars.objects.get(id = id)
    car.delete()
    return redirect('/inventary/')

@login_required
def to_junk(request, id):
    car = Cars.objects.get(id = id)
    car.waiting = False
    car.save()
    car_to_junk = JunkCars(car = car)
    car_to_junk.save()
    return redirect('/inventary/')

@login_required
def scratched(request, id):
    junkcar = JunkCars.objects.get(id = id)
    if request.method == "POST":
        junkcar.waiting = False
        junkcar.scratched_date = datetime.date.today()
        junkcar.save()
        if 'rims' in request.POST:
            print(request.POST['rims'])
            print(datetime.date.today())
        else:
            print('No hay rims')
        return redirect('/inventary/')
    junkcar = JunkCars.objects.get(id = id)
    car = Cars.objects.get(id = junkcar.car.id)
    context = {'form': ShowCarsForm(instance=car)}
    #junkcar.waiting = False
    #junkcar.save()
    return render(request, 'junk.html', context)


#JSON Responses
def models(request):
    data = json.loads(request.body)
    models = Models.objects.filter(brand__id=data['user_id'])
    print(models.values("id", "name"))
    return JsonResponse(list(models.values("id", "name")), safe=False)

def parts_sell(request):
    return render(request, 'parts.html')

def chart_prueba(request):
    return render(request, 'chart_mio.html')