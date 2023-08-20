from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
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
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.views.generic import ListView
from weasyprint import HTML, CSS
import os
from django.conf import settings

# Create your views here.
# cars = form.save(commit=false)

# Generacion de Facturas para partes vendidas

def pdf_invoice_parts(request, *args, **kwargs):
    code = kwargs.get('code')
    invoice = get_object_or_404(Invoices, code = code)

    invoices_parts = PartsByInvoices.objects.filter(invoice = invoice).all()
    print(invoices_parts)

    #Data
    context = {'invoice': invoice}
    context |= {'invoices_parts': invoices_parts}
    
    template_path = 'invoice_parts.html'
    
    template = get_template(template_path)
    html = template.render(context)
    css_basic = os.path.join(settings.BASE_DIR, 'inventary/static/assets/css/invoice.css')
    css_bootstrap = os.path.join(settings.BASE_DIR, 'inventary/static/assets/css/plugins/bootstrap.min.css')
    pdf = HTML(string=html).write_pdf(stylesheets=[CSS(css_bootstrap)]) 
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="invoice-{code}.pdf"'
    return response

# Creacion de facturas de carros vendidos 
def pdf_invoice_cars_sold(request, *args, **kwargs):
    pk = kwargs.get('pk')
    car = get_object_or_404(SoldCars, pk=pk)

    template_path = 'invoice_cars_sold.html'
    context = {'car': car}
    template = get_template(template_path)
    html = template.render(context)
    css_basic = os.path.join(settings.BASE_DIR, 'inventary/static/assets/css/invoice.css')
    css_bootstrap = os.path.join(settings.BASE_DIR, 'inventary/static/assets/css/plugins/bootstrap.min.css')
    pdf = HTML(string=html).write_pdf(stylesheets=[CSS(css_bootstrap)]) 
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="report.pdf"'
    return response

#Vista basada en clase para obtener la lista de datos
class CustomerListView(ListView):
    model = Customer
    template_name = 'customer_main.html'

#Vista para mostrar el contenido dentro del PDF de manera dinamica
def customer_render_pdf_view(request, *args, **kwargs):
    pk = kwargs.get('pk')
    customer = get_object_or_404(Customer, pk=pk)

    template_path = 'pdf2.html'
    context = {'customer': customer}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    #para descargalo se usa este codigo de abajo:
    #response['Content-Disposition'] = 'attachment; filename="report.pdf"'

    # Y para verlo en el navegador sin descargarlo aun se usa este codigo:
    response['Content-Disposition'] = 'filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

#Prueba de creacion de PDF
def render_pdf_view(request):
    template_path = 'pdf1.html'
    context = {'myvar': 'this is your template context'}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    #para descargalo se usa este codigo de abajo:
    #response['Content-Disposition'] = 'attachment; filename="report.pdf"'

    # Y para verlo en el navegador sin descargarlo aun se usa este codigo:
    response['Content-Disposition'] = 'filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

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
    #
    try:
        stock = Stock.objects.get()
    except:
        stock = Stock()
        stock.save()

    context |={'stock': stock}
    #Revenue Data 
    cars_costs = 0
    last_month_cars_costs = 0
    cars_revenue = 0
    last_month_cars_revenue = 0
    parts_revenue = 0
    last_month_parts_revenue = 0
    
    sold_parts = SoldParts.objects.all()
    cars = Cars.objects.all()
    sold_cars = SoldCars.objects.all()

    for sold_part in sold_parts:
        parts_revenue += sold_part.price
        if sold_part.sold_date > first_day:
            last_month_parts_revenue += sold_part.price
 
    for sold_car in sold_cars:
        cars_revenue += sold_car.price
        if sold_car.date > first_day:
            last_month_cars_revenue += sold_car.price

    for car in cars:
        cars_costs += car.cost
        if car.entry_date > first_day:
            last_month_cars_costs += car.cost


    total_revenue = parts_revenue + cars_revenue
    last_month_revenue = last_month_cars_revenue + last_month_parts_revenue

    total_profit = total_revenue - cars_costs
    last_month_profit = last_month_revenue - last_month_cars_costs

    context |= {'total_revenue': total_revenue, 'last_month_revenue': last_month_revenue}
    context |= {'total_profit': total_profit, 'last_month_profit': last_month_profit}

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

    try:
        cars1 = SoldCars.objects.filter(date__month = month[0], date__year = year[0]).all()
        total_price1 = 0
        for car in cars1:
            total_price1 += car.price
        total_price1 /= 1000
    except:
        total_price1 = 0

    cars_data.append(total_price1)

    try:
        cars2 = SoldCars.objects.filter(date__month = month[1], date__year = year[1]).all()
        total_price2 = 0
        for car in cars2:
            total_price2 += car.price
        total_price2 /= 1000
    except:
        total_price2 = 0

    cars_data.append(total_price2)

    try:
        cars3 = SoldCars.objects.filter(date__month = month[2], date__year = year[2]).all()
        total_price3 = 0
        for car in cars3:
            total_price3 += car.price
        total_price3 /= 1000
    except:
        total_price3 = 0

    cars_data.append(total_price3)

    try:
        cars4 = SoldCars.objects.filter(date__month = month[3], date__year = year[3]).all()
        total_price4 = 0
        for car in cars4:
            total_price4 += car.price
        total_price4 /= 1000
    except:
        total_price4 = 0

    cars_data.append(total_price4)

    try:
        cars5 = SoldCars.objects.filter(date__month = month[4], date__year = year[4]).all()
        total_price5 = 0
        for car in cars5:
            total_price5 += car.price
        total_price5 /= 1000
    except:
        total_price5 = 0

    cars_data.append(total_price5)

    try:
        cars6 = SoldCars.objects.filter(date__month = month[5], date__year = year[5]).all()
        total_price6 = 0
        for car in cars6:
            total_price6 += car.price
        total_price6 /= 1000
    
    except:
        total_price6 = 0

    cars_data.append(total_price6)

    try:
        cars7 = SoldCars.objects.filter(date__month = month[6], date__year = year[6]).all()
        total_price7 = 0
        for car in cars7:
            total_price7 += car.price
        total_price7 /= 1000
    except:
        total_price7 = 0

    cars_data.append(total_price7)

    try:
        cars8 = SoldCars.objects.filter(date__month = month[7], date__year = year[7]).all()
        total_price8 = 0
        for car in cars8:
            total_price8 += car.price
        total_price8 /= 1000
    except:
        total_price8 = 0

    cars_data.append(total_price8)

    try:
        cars9 = SoldCars.objects.filter(date__month = month[8], date__year = year[8]).all()
        total_price9 = 0
        for car in cars9:
            total_price9 += car.price
        total_price9 /= 1000
    except:
        total_price9 = 0

    cars_data.append(total_price9)

    context |= {'cars_data': cars_data}


#Incomes and Counters for Sales Ratio
    parts_data = []
    rims_data = []
    tires_data = []
    catalysts_data = []
    engines_data = []

    #Counters Array
    sr_rims = []
    sr_tires = []
    sr_catalysts = []
    sr_engines = []
    sr_parts = []
    for i in range(0, 9, 1):
        print(i)
        rims_price = 0
        rims_counter = 0
        tires_price = 0
        tires_counter = 0
        catalysts_price = 0
        catalysts_counter = 0
        engines_price = 0
        engines_counter = 0
        parts_price = 0
        parts_counter = 0
        try:
            parts = SoldParts.objects.filter(sold_date__month = month[i], sold_date__year = year[i]).all()
            for part in parts:
                if part.part_type.name == "Rims":
                    rims_price += part.price
                    rims_counter += part.quantity 
                elif part.part_type.name == "Tires":
                    tires_price += part.price
                    tires_counter += part.quantity
                elif part.part_type.name == "Catalyst":
                    catalysts_price += part.price
                    catalysts_counter += part.quantity
                elif part.part_type.name == "Engines":
                    engines_price += part.price
                    engines_counter += part.quantity
                else:
                    parts_price += part.price
                    parts_counter += part.quantity
            
            rims_price /= 1000
            tires_price /= 1000
            catalysts_price /= 1000
            engines_price /= 1000
            parts_price /= 1000
            #print(rim_price)
        except:
            pass

        #Counters for Sales Ratio
        sr_tires.append(tires_counter)
        sr_rims.append(rims_counter)
        sr_engines.append(engines_counter)
        sr_catalysts.append(catalysts_counter)
        sr_parts.append(parts_counter)

        #Incomes    
        parts_data.append(parts_price)
        rims_data.append(rims_price)
        tires_data.append(tires_price)
        catalysts_data.append(catalysts_price)
        engines_data.append(engines_price)

    print(parts_data)
    print(tires_data)
    print(rims_data)
    print(catalysts_data)
    print(engines_data)
    context |= {'parts_data': parts_data}
    context |= {'rims_data': rims_data}
    context |= {'tires_data': tires_data}
    context |= {'engines_data': engines_data}
    context |= {'catalysts_data': catalysts_data}

    #Sales Ratio Data
    context |= {'sr_tires': sr_tires}
    context |= {'sr_rims': sr_rims}
    context |= {'sr_engines': sr_engines}
    context |= {'sr_catalysts': sr_catalysts}
    context |= {'sr_parts': sr_parts}


    
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
    try: 
        if entry_car.title:
            title_sufix = entry_car.title.name.split('.')[-1]
            if not (str.lower(title_sufix) == 'pdf'):
                error_messages.append('Title: Unknow file type. Select a PDF file.')
                return render(request, 'entry.html', context)   
        
            entry_car.title = rename_file(entry_car.title, entry_car.inventary_number, entry_car.entry_date)
            print(entry_car.title.name)
    except:
        print("Doesn't exists pdf file.")
    try:
        if entry_car.image:
            image_sufix = entry_car.image.name.split('.')[-1]
            if not (str.lower(image_sufix) == 'jpeg' or str.lower(image_sufix) == 'jpg' or str.lower(image_sufix) == 'png'):
                error_messages.append('Image: Unknow image type. Select a JPG or PNG file.')
                return render(request, 'entry.html', context)
    
            entry_car.image = rename_file(entry_car.image, entry_car.inventary_number, entry_car.entry_date)
            print(entry_car.year)
    except:
        print("Doesn't exists image.")

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
        return redirect('/inventary/cars')

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
        return redirect('/inventary/cars')
    
    car.waiting = False
    car.save()
    car_to_junk = JunkCars(car = car)
    car_to_junk.save()
    return redirect('/inventary/cars')

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
        return redirect('/inventary/junked')
    
    context = {'form': ShowCarsForm(instance=junkcar.car)}
    return render(request, 'junk.html', context)


#JSON Responses
def models(request):
    data = json.loads(request.body)
    models = Models.objects.filter(brand__id=data['user_id'])
    print(models.values("id", "name"))
    return JsonResponse(list(models.values("id", "name")), safe=False)

@login_required
def parts_sell(request):
    try:
        stock = Stock.objects.get()
    except:
        stock = Stock()
        stock.save()
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
                if not (str.lower(buyer.name) == str.lower(request.POST['name']) and (str.lower(buyer.last_name) == str.lower(request.POST['last_name']))):
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
                if not (str.lower(buyer.name) == str.lower(request.POST['name']) and (str.lower(buyer.last_name) == str.lower(request.POST['last_name']))):
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
            
            if not quantity <= stock.catalysts:
                return redirect('/inventary/')
            #if not (request.POST['date'] <= datetime.date.today):
                #return redirect('/parts/')
            #buyer = Buyers.objects.filter(dni = request.POST['dni'])
            try:
                buyer = Buyers.objects.filter(dni = request.POST['dni']).get()
                if not (str.lower(buyer.name) == str.lower(request.POST['name']) and (str.lower(buyer.last_name) == str.lower(request.POST['last_name']))):
                    error_messages.append(f'Other buyer already have the {buyer.dni} DNI.')
                    print('Error comprador')
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
                if not (str.lower(buyer.name) == str.lower(request.POST['name']) and (str.lower(buyer.last_name) == str.lower(request.POST['last_name']))):                    
                    error_messages.append(f'Other buyer already have the {buyer.dni} DNI.')
                    print('error comprador')
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
            print('others')
            if not (request.POST['name'] != '' and request.POST['last_name'] != '' and request.POST['dni'] != '' and request.POST['date'] != '' and request.POST['part_name'] != '' and request.POST['price'] != '' and request.POST['car_id'] != ''):
              print('Error')
              return redirect('/parts/')

            try:

                price = float(request.POST['price'])
                car = Cars.objects.filter(inventary_number = request.POST['car_id']).get()
                print('Convertido')
            except:
                print('Errores numerico o ID de auto.')
                return redirect('/parts/')  
            
            #if not (request.POST['date'] <= datetime.date.today):
                #return redirect('/parts/')
            #buyer = Buyers.objects.filter(dni = request.POST['dni'])
            try:
                buyer = Buyers.objects.filter(dni = request.POST['dni']).get()
                if not (str.lower(buyer.name) == str.lower(request.POST['name']) and (str.lower(buyer.last_name) == str.lower(request.POST['last_name']))):
                    error_messages.append(f'Other buyer already have the {buyer.dni} DNI.')
                    print('error comprador.')
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

@login_required
def chart_prueba(request):
    numeros = [20, 30, 40, 100, 70, 90]
    return render(request, 'chart_mio.html', {'numeros':numeros})

@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required
def user_settings(request):
    return render(request, 'user_settings.html')

#Tabla Cars
@login_required
def inventary_cars(request):
    q = request.GET.get('search_cars', '')
    if q:
        multiple_q = Q(inventary_number__icontains=q) | Q(cost__icontains=q)
        cars = Cars.objects.filter(multiple_q, waiting=True).order_by('-entry_date')
    else:
        cars = Cars.objects.filter(waiting=True).order_by('-entry_date')
    
    car_counter = cars.count()

    # Paginacion
    page = request.GET.get('page', 1)
    paginator = Paginator(cars, 50)

    try:
        cars_page = paginator.page(page)
    except:
        raise Http404

    junkcar_counter = JunkCars.objects.filter(waiting=True).count()

    context = {
        'cars': cars_page,
        'paginator': paginator,
        'car_counter': car_counter,
        'junkcar_counter': junkcar_counter,
        'q': q
    }
    return render(request, 'inventary_cars.html', context)

#Tabla Pendientes
@login_required
def inventary_pendings(request):
    q = request.GET.get('pendings_search', '')
    if q:
        multiple_q = Q(car__inventary_number__icontains=q)
        pendings = JunkCars.objects.filter(multiple_q, waiting=True).order_by('-to_junk_date')
    else:
        pendings = JunkCars.objects.filter(waiting=True).order_by('to_junk_date')
    page = request.GET.get('page', 1)

    try:
        paginator_pendings = Paginator(pendings, 60)
        pendings = paginator_pendings.page(page)
    except:
        raise Http404

    junkcar_counter = JunkCars.objects.filter(waiting = True).count()
    context = {'junkcars': pendings,'paginator_pendings':paginator_pendings,'junkcar_counter': junkcar_counter}

    return render(request, 'inventary_pendings.html', context)

#Tabla Junked Cars
@login_required
def inventary_junked(request):
    q = request.GET.get('junked_search', '')
    if q:
        multiple_q = Q(car__inventary_number__icontains=q)
        scratched_cars = JunkCars.objects.filter(multiple_q, waiting=False, out=False).order_by('-scratched_date')
    else:       
        scratched_cars = JunkCars.objects.filter(waiting=False, out=False).order_by('-scratched_date')
    page = request.GET.get('page', 1)

    try:
        paginator_junked = Paginator(scratched_cars, 60)
        scratched_cars = paginator_junked.page(page)
    except:
        raise Http404

    junkcar_counter = JunkCars.objects.filter(waiting = True).count()
    context = {'scratched_cars': scratched_cars,'paginator_junked':paginator_junked,'junkcar_counter': junkcar_counter}
    return render(request, 'inventary_junked.html', context)

#Tabla Parts Sold
@login_required
def inventary_parts(request):
    q = request.GET.get('parts_search', '')
    if q:
        multiple_q = Q(code__icontains=q)
        invoices = Invoices.objects.filter(multiple_q).order_by('-date')
    else: 
        invoices = Invoices.objects.all().order_by('-date')
    page = request.GET.get('page', 1)

    try:
        paginator_parts = Paginator(invoices, 60)
        invoices = paginator_parts.page(page)
    except:
        raise Http404

    junkcar_counter = JunkCars.objects.filter(waiting = True).count()
    context = {'invoices': invoices,'paginator_parts':paginator_parts,'junkcar_counter': junkcar_counter}

    return render(request, 'inventary_parts.html', context)


#Vista para mostrar el contenido dentro del PDF de manera dinamica de las Partes
@login_required
def parts_render_pdf_view(request, *args, **kwargs):
    pk = kwargs.get('pk')
    parts = get_object_or_404(SoldParts, pk=pk)

    template_path = 'parts_pdf.html'
    context = {'parts': parts}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    #para descargalo se usa este codigo de abajo:
    #response['Content-Disposition'] = 'attachment; filename="report.pdf"'

    # Y para verlo en el navegador sin descargarlo aun se usa este codigo:
    response['Content-Disposition'] = 'filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


#Tabla Cars Sold
@login_required
def inventary_cars_sold(request):
    q = request.GET.get('cars_sold_search', '')
    if q:
        multiple_q = Q(car__inventary_number__icontains=q)
        cars_sold = SoldCars.objects.filter(multiple_q).order_by('-date')

    else:  
        cars_sold = SoldCars.objects.all().order_by('-date')
    buyers_data = Buyers.objects.all()
    page = request.GET.get('page', 1)

    try:
        paginator_cars_sold = Paginator(cars_sold, 60)
        cars_sold = paginator_cars_sold.page(page)
    except:
        raise Http404

    junkcar_counter = JunkCars.objects.filter(waiting = True).count()
    context = {'cars_sold': cars_sold,'paginator_cars_sold':paginator_cars_sold,'junkcar_counter': junkcar_counter,'buyers_data': buyers_data}

    return render(request, 'inventary_cars_sold.html', context)

#Paginas del Footer
#Licensing
def footer_licensing(request):
    return render(request, 'licensing.html')

def footer_privacy_policy(request):
    return render(request, 'privacy_policy.html')

def footer_about(request):
    return render(request, 'about.html')

def footer_faq(request):
    return render(request, 'faq.html')

def footer_contact(request):
    return render(request, 'contact.html')

@login_required
def sell_parts_new(request):
    options = PartType.objects.all()
    options_select = []
    for option in options:
        options_select.append({"name": option.name, "id": option.id})

    print(options_select)
    context = {'options_select': options_select}
    
    if request.method == "POST":
        #MessagesData
        error_messages = []
        success_messages = []

        #Datos del form
        part_type = request.POST.getlist("part_type")
        quantity = request.POST.getlist("quantity")
        price = request.POST.getlist("price")
        car_id = request.POST.getlist("car_id")
        invoices_code = request.POST['invoices_code']

        #Datos del comprador
        name = request.POST['name']
        last_name = request.POST['last_name']
        dni = request.POST['dni']
        date = request.POST['date']

        if invoices_code == "":
            return render(request, 'sell_parts_new.html', context)
        try:
            invoice = Invoices.objects.filter(code = invoices_code).get()
            if invoice:
                error_messages.append(f'Invoice {invoices_code} already exists.')
                context |= {'error_messages': error_messages}
                return render(request, 'sell_parts_new.html', context)

        except:
            pass
        if not ((len(part_type) == len(quantity)) and (len(part_type) == len(price)) and (len(part_type) == len(car_id))): 
            return render(request, 'sell_parts_new.html', context)
        
        #Comprador
        try:
                buyer = Buyers.objects.filter(dni = dni).get()
                if not (str.lower(buyer.name) == str.lower(name) and (str.lower(buyer.last_name) == str.lower(last_name))):
                    error_messages.append(f'Other buyer already have the {buyer.dni} DNI.')
                    print('error comprador.')
                    context |= {'error_messages': error_messages}
                    return render(request, 'sell_parts_new.html', context)
        except:
            print('Comprador nuevo')
            buyer = Buyers(name = name, last_name = last_name, dni = dni)
            

        #Partes vendidas
        part_quantity = 0
        total_amount = 0
        sold_parts_list = []
        for i in range(0, len(part_type)):
            try:
                car = Cars.objects.filter(inventary_number = car_id[i]).get()
            except:
                error_messages.append(f"Car {car_id[i]} does not exists.")
                context |= {'error_messages': error_messages}
                return render(request, 'sell_parts_new.html', context)
            
            try:
                part_type_for = PartType.objects.filter(id = part_type[i]).get()
            except:
                error_messages.append(f"The selected part type is wrong!")
                context |= {'error_messages': error_messages}
                return render(request, 'sell_parts_new.html', context)

            sold_part = SoldParts(name = "", car = car, part_type = part_type_for, buyer = buyer, price = price[i], quantity = quantity[i], sold_date = date)

            total_amount += int(price[i])

            sold_parts_list.append(sold_part)

            print(f'{sold_part.part_type.name} --- {sold_part.quantity}')
            part_quantity += int(sold_part.quantity)
        
        #Invoice Generator
        invoice = Invoices(code = invoices_code, date = date, total_amount = total_amount, parts_quantity = part_quantity, buyer = buyer)
        
        #Guardado de Datos
        buyer.save()
        invoice.save()
        


        #Relacion partes x factura
        for part in sold_parts_list:
            part.save()
            sold_by_invoice = PartsByInvoices(sold_part = part, invoice = invoice)
            sold_by_invoice.save()

        success_messages.append(f"Invoice {invoices_code} has been created successfully.")
        context |= {'success_messages': success_messages}
        print(success_messages)
        return render(request, 'sell_parts_new.html', context)
    
    
    return render(request, 'sell_parts_new.html', context)

@login_required
def add_brands(request):
    success_messages = []
    error_messages = []
    brands = Brands.objects.all()
    if request.method == "POST":
        brand_new = request.POST['brand']
        print(brand_new)
        print(brands)
        addBrand = True
        for brand in brands:
            if str.lower(brand.name) == str.lower(brand_new):
                addBrand = False
                error_messages.append(f'{brand_new} already exists.')
                break
        
        if addBrand:
            new_brand = Brands(name = brand_new)
            new_brand.save()
            success_messages.append(f'Brand {brand_new} successfully add.')
        
    context = {'brands': brands, 'error_messages': error_messages, 'success_messages': success_messages}
    
    return render(request, 'add_brands.html', context);

@login_required
def add_models(request):
    success_messages = []
    error_messages = []
    brands = Brands.objects.all()

    if request.method == "POST":
        model_brand = request.POST['brand']
        model_new = request.POST['model']
        print(model_new)
        addModel = True

        try:
            brand = Brands.objects.filter(id = model_brand).get()
        except:
            addModel = False

        if addModel:
            models = Models.objects.filter(brand = brand)
            for model in models:
                if str.lower(model.name) == str.lower(model_new):
                    addModel = False
                    error_messages.append(f'{model_new} already exists.')
                    break

        if addModel:
            new_model = Models(brand = brand,name = model_new)
            new_model.save()
            success_messages.append(f'Model {model_new} successfully add to {brand.name}.')
        
    context = {'brands': brands, 'error_messages': error_messages, 'success_messages': success_messages}
    return render(request, 'add_models.html', context);

@login_required
def add_parts(request): 
    success_messages = []
    error_messages = []
    parts = PartType.objects.all()
    if request.method == "POST":
        part_new = request.POST['part_name']
        print(part_new)
        print(parts)
        addPart = True
        for part in parts:
            if str.lower(part.name) == str.lower(part_new):
                addPart = False
                error_messages.append(f'{part_new} already exists.')
                break
        
        if addPart:
            new_part = PartType(name = part_new)
            new_part.save()
            success_messages.append(f'Part {part_new} successfully add.')
        
    context = {'parts': parts, 'error_messages': error_messages, 'success_messages': success_messages}
    return render(request, 'add_parts.html', context);

