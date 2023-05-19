from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import IntegrityError
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import Http404
from django.db.models import Q
from django.utils import timezone
from . import utils
import pandas as pd
import numpy as np
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
            context = {'signinform': AuthenticationForm(), 'messages': messages}            
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


#404 Error
def error404(request):
    return render(request, '404.html')


#Views
@login_required
def home(request):
    today = timezone.localtime(timezone.now())
    first_day = utils.get_first_day(today.year, today.month)
    context = {}
    #Data for counters
    pendings_for_junk = JunkCars.objects.filter(waiting = True).count()
    total_junked_cars = JunkCars.objects.filter(scratched_date__isnull = False).count()
    
    remove_parts = RemoveParts.objects.all()
    remove_parts_last_month = RemoveParts.objects.filter(date__range=(first_day, today))
    total_rims_and_tires = 0
    rims_and_tires_last_month = 0
    total_catalyst = 0
    total_engines = 0
    total_rims = 0
    total_tires = 0 

    for parts in remove_parts:
        if parts.date > first_day:
            rims_and_tires_last_month += parts.rims + parts.tires
        total_rims_and_tires += parts.rims + parts.tires
        total_catalyst += parts.catalyst
        total_engines += parts.engine
        total_tires += parts.tires
        total_rims += parts.rims

    total_cars = Cars.objects.filter(waiting = True).count()
    total_cars += JunkCars.objects.filter(waiting=True).count()

    #Data for Inventary Chart
    context |= {'total_cars': total_cars, 'total_engines': total_engines, 'total_rims': total_rims, 'total_tires': total_tires, 'total_catalyst': total_catalyst}
    context |= {'total_rims_and_tires': total_rims_and_tires, 'rims_and_tires_last_month': rims_and_tires_last_month}
    context |= {'pendings_for_junk': pendings_for_junk}
    context |= {'total_junked_cars': total_junked_cars}


    #Data for All profit chart
    cars_data = []
    categories_all_profit = []
    year = []
    month = []
    for month_ in range(8, -1, -1):
        month_to_function = today.month - month_
        year_ = today.year
        if month_to_function <=0:
            month_to_function += 12
            year_ = today.year - 1
        year.append(year_)
        month.append(month_to_function)
        categories_all_profit.append(utils.return_month_name(month_to_function))
    print(categories_all_profit)
    print(year)

    context |= {'categories_all_profit': categories_all_profit}
    cars1 = SoldCars.objects.filter(date__month = month[0], date__year = year[0]).count()
    cars_data.append(cars1)

    cars2 = SoldCars.objects.filter(date__month = month[1], date__year = year[1]).count()
    cars_data.append(cars2)

    cars3 = SoldCars.objects.filter(date__month = month[2], date__year = year[2]).count()
    cars_data.append(cars3)

    cars4 = SoldCars.objects.filter(date__month = month[3], date__year = year[3]).count()
    cars_data.append(cars4)

    cars5 = SoldCars.objects.filter(date__month = month[4], date__year = year[4]).count()
    cars_data.append(cars5)

    cars6 = SoldCars.objects.filter(date__month = month[5], date__year = year[5]).count()
    cars_data.append(cars6)

    cars7 = SoldCars.objects.filter(date__month = month[6], date__year = year[6]).count()
    cars_data.append(cars7)

    cars8 = SoldCars.objects.filter(date__month = month[7], date__year = year[7]).count()
    cars_data.append(cars8)

    cars9 = SoldCars.objects.filter(date__month = month[8], date__year = year[8]).count()
    cars_data.append(cars9)

    context |= {'cars_data': cars_data}

    
    return render(request, 'index.html', context)

@login_required
def inventary(request):
    car_counter = Cars.objects.filter(waiting = True).count()
    cars = Cars.objects.filter(waiting = True).all()
    page = request.GET.get('page', 1)

    #Data 
    cars = Cars.objects.filter(waiting=True).order_by('-entry_date')
    pendings = JunkCars.objects.filter(waiting=True).order_by('to_junk_date')
    scratched_cars = JunkCars.objects.filter(waiting=False, out=False).order_by('-scratched_date')
    parts_sold = SoldParts.objects.all().order_by('-sold_date')
    cars_sold = SoldCars.objects.all().order_by('-date')
    try:
        paginator = Paginator(cars, 1)
        cars = paginator.page(page)
    except:
        raise Http404


    junkcar_counter = JunkCars.objects.filter(waiting = True).count()
    context = {'junkcar_counter': junkcar_counter,'junkcars': pendings,'cars': cars, 'scratched_cars': scratched_cars, 'parts_sold': parts_sold, 'cars_sold': cars_sold,'paginator':paginator, 'car_counter':car_counter}

    return render(request, 'inventary.html', context)


@login_required
def entry(request):
    validate = True
    error_messages = []
    success_messages = []
    context = {'form': CarsForm(), 'errors': error_messages, 'success': success_messages}
    if request.method == "GET":
        return render(request, 'entry.html', context)
    
    form = CarsForm(request.POST, request.FILES)
    if not form.is_valid():
        error_messages.append('Complete all data')
        return render(request, 'entry.html', context)
    
    entry_car = form.save(commit = False)

    cars = Cars.objects.all()
    if cars:
        for car in cars:
            if car.inventary_number == entry_car.inventary_number or car.vin_number == entry_car.vin_number:
                if car.inventary_number == entry_car.inventary_number:
                    error_messages.append('Inventary number already exist.')
                else:
                    error_messages.append('VIN already exist.')
                return render(request, 'entry.html', context) 

    title_sufix = entry_car.title.name.split('.')[-1]
    if not (str.lower(title_sufix) == 'pdf'):
        error_messages.append('Title: Unknow file type. Select a PDF file.')
        messages.warning(request, "Error select a PDF file.")
        return render(request, 'entry.html', context)   
        
    entry_car.title = rename_file(entry_car.title, entry_car.inventary_number, entry_car.entry_date)
    print(entry_car.title.name)

    image_sufix = entry_car.image.name.split('.')[-1]
    if not (str.lower(image_sufix) == 'jpeg' or str.lower(image_sufix) == 'jpg' or str.lower(image_sufix) == 'png'):
        error_messages.append('Image: Unknow image type. Select a JPG or PNG file.')
        return render(request, 'entry.html', context)
    
    entry_car.image = rename_file(entry_car.image, entry_car.inventary_number, entry_car.entry_date)
    print(entry_car.year)
    try:
        year = int(entry_car.year)
        if not ((year <= 2023) and (year >= 1940)):
            print('Error if year')
            error_messages.append('Year: Enter a valid year(1940-today).')
            return render(request, 'entry.html', context)

    except:
        print('error except')
        error_messages.append('Year: Enter a valid year(1940-today).')
        #messages.warning(request, "Error enter a valid year")
        return render(request, 'entry.html', context)

    print(title_sufix)
    entry_car.save()
    success_messages.append(f'Car {entry_car.inventary_number} added successfully.')
    #probando swet_alert
    messages.success(request, "Car added successfully")
    return render(request, 'entry.html', context)

@login_required
def junk(request):
    context = {'form': CarsForm() }
    return render(request, 'junk.html', context)

#SQL Operations
@login_required
def sell(request, id):
    try:
        car = Cars.objects.get(id=id)
    except:
        return redirect('/404/')
    
    error_messages = []
    success_messages = []
    sold_cars = SoldCars.objects.all()

    for car_sold in sold_cars:
        if car == car_sold.car:
            error_messages.append(f"Car {car.inventary_number} has already been sold.")
            context = {'form': ShowCarsForm(instance=car), 'buyerform': BuyersForm(), 'soldcarform': SoldCarsForm(), 'car': car, 'error_messages': error_messages, 'success_messages': success_messages }
            return render(request, 'sell.html', context) 


    if request.method == "POST":
        try:
            buyer = Buyers.objects.filter(dni = request.POST['dni']).get()
            if not (str.lower(buyer.name) == str.lower(request.POST['name']) and str.lower(buyer.last_name) == str.lower(request.POST['last_name'])):
                error_messages.append(f'Other buyer already have the {buyer.dni} DNI.')
                context = {'form': ShowCarsForm(instance=car), 'buyerform': BuyersForm(), 'soldcarform': SoldCarsForm(), 'car': car, 'error_messages': error_messages, 'success_messages:': success_messages }
                return render(request, 'sell.html', context) 
        except:
            print('Comprador nuevo')
            buyer = Buyers(name = str(request.POST['name']), last_name = request.POST['last_name'], dni = request.POST['dni'], phone_number = request.POST['phone_number'] )
            buyer.save()
        
        sold_car = SoldCars(car = car, buyer = buyer, price = request.POST['price'], date = request.POST['date'])
        car.waiting = False
        car.save()
        buyer.save()
        sold_car.save()
        try:
            junk = JunkCars.objects.get(car = car)
            junk.delete()
        except:
            pass
        
        success_messages.append(f'Car {car.inventary_number} has been added to Sold Cars.')
        return redirect('/inventary/')

    context = {'form': ShowCarsForm(instance=car), 'buyerform': BuyersForm(), 'soldcarform': SoldCarsForm(), 'car': car }
    return render(request, 'sell.html', context) 

@login_required
def delete(request, id):
    try:
        car = Cars.objects.get(id = id)
    except:
        return redirect('/404/')
    
    car.delete()
    messages.success(request, "The car has been deleted.")
    return redirect('/inventary/')

@login_required
def to_junk(request, id):
    try:
        car = Cars.objects.get(id = id)
    except:
        return redirect('/404/')
    
    if car.waiting == False:
        return redirect('/inventary/')
    
    car.waiting = False
    car.save()
    car_to_junk = JunkCars(car = car)
    car_to_junk.save()
    return redirect('/inventary/')

@login_required
def scratched(request, id):
    try:
        junkcar = JunkCars.objects.get(id = id)
    except:
       return redirect('/404/')
    
    if not junkcar.waiting:
        return redirect('/404/')

    if request.method == "POST":
        error_messages = []
        success_messages = []
        try:
            if not (int(request.POST['rims']) <= 4 and int(request.POST['rims']) >= 0) and (int(request.POST['tires']) <= 4 and int(request.POST['tires']) >= 0) and (int(request.POST['catalyst']) <= 5 and int(request.POST['catalyst']) >= 0):
                error_messages.append('Incorrect data')
                context = {'form': ShowCarsForm(instance=junkcar.car), 'error_messages': error_messages, 'success_messages': success_messages}
                return render(request, 'junk.html', context)
        except:
            context = {'form': ShowCarsForm(instance=junkcar.car), 'error_messages': error_messages, 'success_messages': success_messages}
            return render(request, 'junk.html', context)
        
        junkcar.scratched_date = datetime.date.today()
        
        try:
            stock = Stock.objects.get()
        except:
            stock = Stock()

        if 'engine' in request.POST:
            engine = True
            stock.engines += 1
        else:
            engine = False

        stock.tires += int(request.POST['tires'])
        stock.rims += int(request.POST['rims'])
        stock.catalysts += int(request.POST['catalyst'])
        stock.scratched_cars += 1
        stock.save()
        remove_parts = RemoveParts(car = junkcar.car, rims = request.POST['rims'], tires = request.POST['tires'], catalyst = request.POST['catalyst'], engine = engine)
        remove_parts.save()
        junkcar.waiting = False
        junkcar.save()
        return redirect('/inventary/')
    
    context = {'form': ShowCarsForm(instance=junkcar.car)}
    return render(request, 'junk.html', context)


#JSON Responses
def models(request):
    data = json.loads(request.body)
    models = Models.objects.filter(brand__id=data['user_id'])
    print(models.values("id", "name"))
    return JsonResponse(list(models.values("id", "name")), safe=False)

def parts_sell(request):
    try:
        stock = Stock.objects.get()
    except:
        return redirect('/inventary/')
    #Procesamiento de los Forms
    if request.method == "POST":
        error_messages = []
        succes_messages = []
        #Forms Tires
        if request.POST['form_type'] == 'tires':
            if not (request.POST['name'] != '' and request.POST['last_name'] != '' and request.POST['dni'] != '' and request.POST['date'] != '' and request.POST['quantity'] != '' and request.POST['amount'] != ''):
              print('Error')
              error_messages.append('Please, complete all data.')
              return redirect('/parts/')

            try:
                amount = float(request.POST['amount'])
                quantity = int(request.POST['quantity'])
            except:
                print('Errores numerico.')
                error_messages.append('Please check the data of amount and quantity fields.')
                return redirect('/parts/')  
            
            if not quantity <= stock.tires:
                error_messages.append(f'There is not enough tires in stock({stock.tires})')
                return redirect('/inventary/')
            #if not (request.POST['date'] <= datetime.date.today):
                #return redirect('/parts/')
            #buyer = Buyers.objects.filter(dni = request.POST['dni'])
            try:
                buyer = Buyers.objects.filter(dni = request.POST['dni']).get()
                if not (str.lower(buyer.name) == str.lower(request.POST['name']) and str.lower(buyer.last_name) == str.lower(request.POST['last_name'])):
                    error_messages.append(f'Other buyer already have the {buyer.dni} DNI.')
                    context = {'stock': stock, 'error_messages': error_messages, 'success_messages': succes_messages}
                    return render(request, 'parts.html', context)
            except:
                print('Comprador nuevo')
                buyer = Buyers(name = request.POST['name'], last_name = request.POST['last_name'], dni = request.POST['dni'])
                buyer.save()
            print(buyer.dni)

            sold_part = SoldParts(buyer = buyer, quantity = quantity, part_type = 'Tires', price = amount, sold_date = request.POST['date'], name='Tires')
            print(sold_part)
            sold_part.save()
            stock.tires -= quantity
            stock.save()
            print(request.POST['form_type'])
        
        #Forms Rims
        if request.POST['form_type'] == 'rims':
            if not (request.POST['name'] != '' and request.POST['last_name'] != '' and request.POST['dni'] != '' and request.POST['date'] != '' and request.POST['quantity'] != '' and request.POST['amount'] != ''):
              print('Error')
              return redirect('/parts/')

            try:
                amount = float(request.POST['amount'])
                quantity = int(request.POST['quantity'])
            except:
                print('Errores numerico.')
                return redirect('/parts/')  
            
            if not quantity <= stock.rims:
                return redirect('/inventary/')
            #if not (request.POST['date'] <= datetime.date.today):
                #return redirect('/parts/')
            #buyer = Buyers.objects.filter(dni = request.POST['dni'])
            try:
                buyer = Buyers.objects.filter(dni = request.POST['dni']).get()
                if not (str.lower(buyer.name) == str.lower(request.POST['name']) and str.lower(buyer.last_name) == str.lower(request.POST['last_name'])):
                    error_messages.append(f'Other buyer already have the {buyer.dni} DNI.')
                    context = {'stock': stock, 'error_messages': error_messages, 'success_messages': succes_messages}
                    return render(request, 'parts.html', context)
            except:
                print('Comprador nuevo')
                buyer = Buyers(name = request.POST['name'], last_name = request.POST['last_name'], dni = request.POST['dni'])
                buyer.save()
            print(buyer.dni)

            sold_part = SoldParts(buyer = buyer, quantity = quantity, part_type = 'Rims', price = amount, sold_date = request.POST['date'], name='Rims')
            print(sold_part)
            sold_part.save()
            stock.rims -= quantity
            stock.save()
            print(request.POST['form_type'])

        #Forms Catalysts
        if request.POST['form_type'] == 'catalysts':
            if not (request.POST['name'] != '' and request.POST['last_name'] != '' and request.POST['dni'] != '' and request.POST['date'] != '' and request.POST['quantity'] != '' and request.POST['amount'] != ''):
              print('Error')
              return redirect('/parts/')

            try:
                amount = float(request.POST['amount'])
                quantity = int(request.POST['quantity'])
            except:
                print('Errores numerico.')
                return redirect('/parts/')  
            
            if not quantity <= stock.tires:
                return redirect('/inventary/')
            #if not (request.POST['date'] <= datetime.date.today):
                #return redirect('/parts/')
            #buyer = Buyers.objects.filter(dni = request.POST['dni'])
            try:
                buyer = Buyers.objects.filter(dni = request.POST['dni']).get()
                if not (str.lower(buyer.name) == str.lower(request.POST['name']) and str.lower(buyer.last_name) == str.lower(request.POST['last_name'])):
                    error_messages.append(f'Other buyer already have the {buyer.dni} DNI.')
                    context = {'stock': stock, 'error_messages': error_messages, 'success_messages': succes_messages}
                    return render(request, 'parts.html', context)
            except:
                print('Comprador nuevo')
                buyer = Buyers(name = request.POST['name'], last_name = request.POST['last_name'], dni = request.POST['dni'])
                buyer.save()
            print(buyer.dni)

            sold_part = SoldParts(buyer = buyer, quantity = quantity, part_type = 'Catalyst', price = amount, sold_date = request.POST['date'], name='Catalyst')
            print(sold_part)
            sold_part.save()
            stock.catalysts -= quantity
            stock.save()
            print(request.POST['form_type'])

        #Forms Engines
        if request.POST['form_type'] == 'engines':
            if not (request.POST['name'] != '' and request.POST['last_name'] != '' and request.POST['dni'] != '' and request.POST['date'] != '' and request.POST['quantity'] != '' and request.POST['amount'] != ''):
              print('Error')
              return redirect('/parts/')

            try:
                amount = float(request.POST['amount'])
                quantity = int(request.POST['quantity'])
            except:
                print('Errores numerico.')
                return redirect('/parts/')  
            
            if not quantity <= stock.engines:
                return redirect('/inventary/')
            #if not (request.POST['date'] <= datetime.date.today):
                #return redirect('/parts/')
            #buyer = Buyers.objects.filter(dni = request.POST['dni'])
            try:
                buyer = Buyers.objects.filter(dni = request.POST['dni']).get()
                if not (str.lower(buyer.name) == str.lower(request.POST['name']) and str.lower(buyer.last_name) == str.lower(request.POST['last_name'])):
                    error_messages.append(f'Other buyer already have the {buyer.dni} DNI.')
                    context = {'stock': stock, 'error_messages': error_messages, 'success_messages': succes_messages}
                    return render(request, 'parts.html', context)
            except:
                print('Comprador nuevo')
                buyer = Buyers(name = request.POST['name'], last_name = request.POST['last_name'], dni = request.POST['dni'])
                buyer.save()
            print(buyer.dni)

            sold_part = SoldParts(buyer = buyer, quantity = quantity, part_type = 'Engines', price = amount, sold_date = request.POST['date'], name='Engines')
            print(sold_part)
            sold_part.save()
            stock.engines -= quantity
            stock.save()
            print(request.POST['form_type'])

        #Forms Others
        if request.POST['form_type'] == 'others':
            if not (request.POST['name'] != '' and request.POST['last_name'] != '' and request.POST['dni'] != '' and request.POST['date'] != '' and request.POST['part_name'] != '' and request.POST['price'] != '' and request.POST['car_id'] != ''):
              print('Error')
              return redirect('/parts/')

            try:
                price = float(request.POST['price'])
                car = Cars.objects.filter(inventary_number = request.POST['car_id']).get()
            except:
                print('Errores numerico o ID de auto.')
                return redirect('/parts/')  
            
            #if not (request.POST['date'] <= datetime.date.today):
                #return redirect('/parts/')
            #buyer = Buyers.objects.filter(dni = request.POST['dni'])
            try:
                buyer = Buyers.objects.filter(dni = request.POST['dni']).get()
                if not (str.lower(buyer.name) == str.lower(request.POST['name']) and str.lower(buyer.last_name) == str.lower(request.POST['last_name'])):
                    error_messages.append(f'Other buyer already have the {buyer.dni} DNI.')
                    context = {'stock': stock, 'error_messages': error_messages, 'success_messages': succes_messages}
                    return render(request, 'parts.html', context)
            except:
                print('Comprador nuevo')
                buyer = Buyers(name = request.POST['name'], last_name = request.POST['last_name'], dni = request.POST['dni'])
                buyer.save()
            print(buyer.dni)

            sold_part = SoldParts(car = car,buyer = buyer, part_type = 'Others', price = price, sold_date = request.POST['date'], name=request.POST['part_name'])
            print(sold_part)
            sold_part.save()
            print(request.POST['form_type'])

        else:
            return redirect('/parts/')
    context = {'stock': stock}
    return render(request, 'parts.html', context)

def chart_prueba(request):
    numeros = [20, 30, 40, 100, 70, 90]
    return render(request, 'chart_mio.html', {'numeros':numeros})

def profile(request):
    return render(request, 'profile.html')

def user_settings(request):
    return render(request, 'user_settings.html')

#Tabla Cars
def inventary_cars(request):
    car_counter = Cars.objects.filter(waiting = True).count()
    cars = Cars.objects.filter(waiting = True).all()
    page = request.GET.get('page', 1)

    cars = Cars.objects.filter(waiting=True).order_by('-entry_date')
    try:
        paginator = Paginator(cars, 1)
        cars = paginator.page(page)
    except:
        raise Http404
    
    context = {'cars': cars,'paginator':paginator, 'car_counter':car_counter}
    return render(request, 'inventary_cars.html', context)

#Tabla Pendientes
def inventary_pendings(request):

    pendings = JunkCars.objects.filter(waiting=True).order_by('to_junk_date')
    page = request.GET.get('page', 1)

    try:
        paginator_pendings = Paginator(pendings, 1)
        pendings = paginator_pendings.page(page)
    except:
        raise Http404

    junkcar_counter = JunkCars.objects.filter(waiting = True).count()
    context = {'junkcars': pendings,'paginator_pendings':paginator_pendings,'junkcar_counter': junkcar_counter}

    return render(request, 'inventary_pendings.html', context)

#Tabla Junked Cars
def inventary_junked(request):
    scratched_cars = JunkCars.objects.filter(waiting=False, out=False).order_by('-scratched_date')
    page = request.GET.get('page', 1)

    try:
        paginator_junked = Paginator(scratched_cars, 1)
        scratched_cars = paginator_junked.page(page)
    except:
        raise Http404

    context = {'scratched_cars': scratched_cars,'paginator_junked':paginator_junked}
    return render(request, 'inventary_junked.html', context)

#Tabla Parts Sold
def inventary_parts(request):
    parts_sold = SoldParts.objects.all().order_by('-sold_date')
    page = request.GET.get('page', 1)

    try:
        paginator_parts = Paginator(parts_sold, 1)
        parts_sold = paginator_parts.page(page)
    except:
        raise Http404

    context = {'parts_sold': parts_sold,'paginator_parts':paginator_parts}

    return render(request, 'inventary_parts.html', context)

#Tabla Cars Sold
def inventary_cars_sold(request):
    cars_sold = SoldCars.objects.all().order_by('-date')
    page = request.GET.get('page', 1)

    try:
        paginator_cars_sold = Paginator(cars_sold, 1)
        cars_sold = paginator_cars_sold.page(page)
    except:
        raise Http404

    context = {'cars_sold': cars_sold,'paginator_cars_sold':paginator_cars_sold}

    return render(request, 'inventary_cars_sold.html', context)