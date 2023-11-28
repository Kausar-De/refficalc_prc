import os
from unicodedata import category
from django.db.models.aggregates import Avg
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from .decorators import unauthenticated_user, allowed_users
from .models import *
from django.contrib.auth import get_user_model, authenticate, login, logout
from .forms import BuildingForm, FlatForm, CreateUserForm, PictureForm
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _
from .filters import FlatFilter
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

# Create your views here.

@unauthenticated_user
def registerPage(request):
    form = CreateUserForm

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            building = form.cleaned_data.get('first_name')
            mailid = form.cleaned_data.get('email')
            messages.success(request, building + ' was registered successfully!')
            send_mail('Evaluator Registration Successful!', 'Respected User, Thank you for registering your building on our Residential Energy Evaluator! Access it here: refficalcstaging.herokuapp.com', os.environ.get('EMAIL_HOST_USER'), [mailid], fail_silently = True)
            return redirect('login')

    context = {'form':form}

    return render(request, 'calculator/register.html', context)

@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username = username, password = password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username OR Password is incorrect!')
            return render(request, 'calculator/login.html')

    context = {}

    return render(request, 'calculator/login.html', context)

def logoutUser(request):
    logout(request)
    messages.info(request, 'Successfully logged out!')
    return redirect('login')

@login_required(login_url = 'login')
def home(request):
    return render(request, 'calculator/homepage.html')

@login_required(login_url = 'login')
def calculate(request):
    form = FlatForm()

    if request.method == 'POST':
        form = FlatForm(request.POST)
        if form.is_valid():
            category = form.cleaned_data.get('category')
            flats = Flat.objects.filter(category = category)
            flatcount = flats.count()
            if flatcount != 0:
                unitmean = round(flats.aggregate(Avg('units'))['units__avg'], 2)
                billmean = round(flats.aggregate(Avg('billamt'))['billamt__avg'], 2)
            else:
                unitmean = 0
                billmean = 0
                

            stock = form.save(commit = False)
            stock.building = request.user
            stock.save()
 
            units = form.cleaned_data.get('units')
            bill = form.cleaned_data.get('billamt')
            flatname = form.cleaned_data.get('name')
            if flatcount != 0: 
                unitdiff = round((unitmean - units), 2)
                billdiff = round((billmean - bill), 2)
                if unitdiff >= 0 and billdiff >= 0:
                    messages.info(request, 'Compared to buildings of same category, you saved ' + str(unitdiff) + ' units on average, and you saved ' + str(billdiff) + ' INR in electricity bills!')
                    resultmsg = 'Compared to buildings of same category, you saved ' + str(unitdiff) + ' units on average, and you saved ' + str(billdiff) + ' INR in electricity bills!'
                elif unitdiff >= 0 and billdiff < 0:
                    messages.info(request, 'Compared to buildings of same category, you saved ' + str(unitdiff) + ' units on average, but, you spent ' + str(abs(billdiff)) + ' INR more in electricity bills!')
                    resultmsg = 'Compared to buildings of same category, you saved ' + str(unitdiff) + ' units on average, but, you spent ' + str(abs(billdiff)) + ' INR more in electricity bills!'
                elif unitdiff < 0 and billdiff >= 0:
                    messages.info(request, 'Compared to buildings of same category, you consumed ' + str(abs(unitdiff)) + ' more units on average, but, you saved ' + str(billdiff) + ' INR in electricity bills!')
                    resultmsg = 'Compared to buildings of same category, you consumed ' + str(abs(unitdiff)) + ' more units on average, but, you saved ' + str(billdiff) + ' INR in electricity bills!'
                elif unitdiff < 0 and billdiff < 0:
                    messages.info(request, 'Compared to buildings of same category, you consumed ' + str(abs(unitdiff)) + ' more units on average, and you spent ' + str(abs(billdiff)) + ' INR more in electricity bills!')
                    resultmsg = 'Compared to buildings of same category, you consumed ' + str(abs(unitdiff)) + ' more units on average, and you spent ' + str(abs(billdiff)) + ' INR more in electricity bills!'
                
                send_mail('Flat Update Successful!', str('Respected User, Your flat, ' + str(flatname) + ', was uploaded to our database successfully! Here is how you performed: ' + str(resultmsg)), os.environ.get('EMAIL_HOST_USER'), [request.user.email], fail_silently = True)

                return redirect('/result')
            else:
                messages.info(request, 'No other flats of the same category yet!')
                resultmsg = 'No other flats of the same category yet!'

                send_mail('Flat Update Successful!', str('Respected User, Your flat, ' + str(flatname) + ', was uploaded to our database successfully! Here is how you performed: ' + str(resultmsg)), os.environ.get('EMAIL_HOST_USER'), [request.user.email], fail_silently = True)

                return redirect('/result')
    
    context = {'form':form}

    return render(request, 'calculator/calculate.html', context)

@login_required(login_url = 'login')
def result(request):
    context = {}
    return render(request, 'calculator/result.html', context)

@login_required(login_url = 'login')
def updateFlat(request, pk):
    flat = Flat.objects.get(id = pk)
    form = FlatForm(instance = flat)

    if request.method == 'POST':
        form = FlatForm(request.POST, instance = flat)
        if form.is_valid():
            form.save()
            return redirect('/user')
    
    context = {'form':form}

    return render(request, 'calculator/calculate.html', context)

@login_required(login_url = 'login')
def updateAppliance(request, pk):
    flat = Flat.objects.get(id = pk)
    applcount = flat.appliances
    ApplianceFormSet = inlineformset_factory(Flat, ApplianceData, exclude = ['flat'], labels = {'appltype': _('Appliance Type'), 'modelname': _('Model Name/No.'), 'rating': _('Power Rating (Kilowatts)'),}, extra = applcount, max_num = applcount)
    formset = ApplianceFormSet(instance = flat)

    if request.method == 'POST':
        formset = ApplianceFormSet(request.POST, instance = flat)
        if formset.is_valid():
            formset.save()
            return redirect('/user')

    context = {'form':formset}
    return render(request, 'calculator/appliance_form.html', context)     

@login_required(login_url = 'login')
def removeFlat(request, pk):
    flat = Flat.objects.get(id = pk)

    if request.method == 'POST':
        flat.delete()
        return redirect('/')
    
    context = {'flat':flat}
    
    return render(request, 'calculator/remove.html', context)

@login_required(login_url = 'login')
def benchmark(request, pk):
    flat = Flat.objects.get(id = pk)
    flats = Flat.objects.filter(building = request.user)
    flatcount = flats.count()
    if flatcount != 0: 
        mean = round(flats.aggregate(Avg('units'))['units__avg'], 2)
    else:
        mean = 0

    lastyrunits = flat.lastyr_units.split(", ")
    twoyrbfrunits = flat.twoyrbfr_units.split(", ")
    threeyrbfrunits = flat.threeyrbfr_units.split(", ")

    flatEPI = round((flat.units / (flat.area / 10.764)), 3)
    flatPOC = round((flat.units / flat.occupants), 3)

    allflatsincat = Flat.objects.filter(category = flat.category)
    
    allunits = list(i.units for i in allflatsincat)
    allareas = list((i.area / 10.764) for i in allflatsincat)
    alloccupants = list(i.occupants for i in allflatsincat)

    meanEPI = round((sum([allunits[i] / allareas[i] for i in range(allflatsincat.count())]) / allflatsincat.count()), 3)
    percEPI = round((((meanEPI - flatEPI) * 100) / flatEPI), 2)

    meanPOC = round((sum([allunits[i] / alloccupants[i] for i in range(allflatsincat.count())]) / allflatsincat.count()), 3)
    percPOC = round((((meanPOC - flatPOC) * 100) / flatPOC), 2)

    context = {'flat':flat, 'lastyrunits':lastyrunits, 'twoyrbfrunits':twoyrbfrunits, 'threeyrbfrunits':threeyrbfrunits, 'flats':flats, 'flatcount':flatcount, 'mean':mean, 'flatEPI':flatEPI, 'flatPOC':flatPOC, 'allflatsincat':allflatsincat, 'percEPI': percEPI, 'percPOC': percPOC}    
   
    return render(request, 'calculator/benchmark.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Building'])
def buildingPage(request):
    flats = Flat.objects.filter(building = request.user)
    flatcount = flats.count()
    if flatcount != 0: 
        mean = round(flats.aggregate(Avg('units'))['units__avg'], 2)
    else:
        mean = 0

    context = {'flats':flats, 'flatcount':flatcount, 'mean':mean}

    return render(request, 'calculator/user.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Building'])
def accountSettings(request):
    building = request.user
    form1 = BuildingForm(instance = building)
    form2 = PictureForm(instance = building.buildingdata)

    if request.method == 'POST':
        form1 = BuildingForm(request.POST, instance = building)
        form2 = PictureForm(request.POST, request.FILES, instance = building.buildingdata)
        if form1.is_valid and form2.is_valid():
            form1.save()
            form2.save()
            messages.info(request, 'Changes saved successfully!')
            return redirect('/user')

    context = {'form1':form1, 'form2':form2}

    return render(request, 'calculator/account_settings.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['Admin'])
def database(request):
    buildings = get_user_model().objects.filter(is_staff = False)
    flats = Flat.objects.all()
    usercount = buildings.count()
    flatcount = flats.count()
    if flatcount != 0: 
        mean = round(flats.aggregate(Avg('units'))['units__avg'], 2)
    else:
        mean = 0
    
    context = {'buildings':buildings, 'flats':flats, 'usercount':usercount, 'flatcount':flatcount, 'mean':mean}

    return render(request, 'calculator/database.html', context)

@login_required(login_url = 'login')
def building(request, pk):
    buildings = get_user_model().objects.get(id = pk)
    flats = Flat.objects.filter(building = buildings)
    flatcount = flats.count()

    myFilter = FlatFilter(request.GET, queryset = flats)
    flats = myFilter.qs

    context = {'buildings':buildings, 'flats':flats, 'flatcount':flatcount, 'myFilter':myFilter}

    return render(request, 'calculator/building.html', context)

@login_required(login_url = 'login')
def flats(request):
    flats = Flat.objects.all()

    context = {'flats':flats}

    return render(request, 'calculator/flats.html', context)

@login_required(login_url = 'login')
def iotReading(request):
    return render(request, 'calculator/iot.html')