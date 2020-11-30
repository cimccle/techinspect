from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.shortcuts import render
from django.utils.html import mark_safe
from pages import forms
from pages import utils
from pages.models import Vehicle, Inspection
import datetime

def login_render(request):
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            #IMPORTANT: TO ACCESS FORM DATA ALWAYS USE cleaned_data['name of field']
            try:
                if utils.login(form.cleaned_data['username'], form.cleaned_data['password']):
                    return HttpResponseRedirect('garage/' + utils.find_user_uuid(form.cleaned_data['username']) + '/') 
                
                else:
                    messages.error(request, "Login failed due to incorrect username/password")
            except ObjectDoesNotExist:
                    messages.error(request, mark_safe("Your username isn't associated with an account. </br>Click <a href='signup/'>here</a> to create an account."))
    else:
        form = forms.LoginForm()
    return render(request, 'login/index.html', {'form': form})

def homepage_render(request, uuid):
    return render(request, 'profile/profile.html', {'uuid': uuid})

def profile_render(request, uuid):
    if request.method == 'POST':
        password_form = forms.PasswordChangeForm(request.POST)
        if password_form.is_valid() and password_form.verify_old_password(uuid) and password_form.verify_new_password():
            try:
                user = utils.get_user(uuid)
                user.set_password(password_form.cleaned_data['password'])
                user.save()
                print(user)
            except Exception:
                print("Something went wrong :(")
        else:
            print("Checks failing for some reason")
    else:
        password_form = forms.PasswordChangeForm()

    form = forms.ProfileForm(instance=utils.get_user(uuid)) #Assumes user is logged in.
    profile_image = utils.get_user(uuid).image
    return render(request, 'profile/profile.html', {'profile_image': profile_image, 'profile_form': form, 'password_form': password_form, 'uuid': uuid})

def inspection_render(request, uuid):
    if request.method == 'POST':
        form = forms.InspectionForm(request.POST)
        form.set_queryset(uuid)
        if form.is_valid():
            print("Getting here")
            form.create()
            form = forms.InspectionForm()
            form.set_queryset(uuid)
        else:
            print("Form failed for some reason")
    else:
        form = forms.InspectionForm(uuid)
    return render(request, 'inspections/inspections.html', {'inspection_form': form, 'uuid': uuid})


def garage_render(request, uuid):
    cars = Vehicle.objects.filter(UUID=utils.get_user(uuid))
    today = datetime.date.today()
    yearDiffs = []
    for i in range(0, len(cars)):
        if(cars[i].inspectionID):
            yearDiffs.append(today.year - cars[i].inspectionID.inspectionDate.year)
        else:
            yearDiffs.append(5) #Basically just needs to be a number that fails the check
       
    myZips = zip(cars, yearDiffs)
    return render(request, 'cars/garage.html', {'garage_cars': cars, 'myZips': myZips, 'uuid': uuid})

def cars_render(request, uuid):
    if request.method == 'POST':
        form = forms.VehicleForm(request.POST, request.FILES)
        print(uuid)
        if form.is_valid():
            form.create(uuid)
    else:
        form = forms.VehicleForm()
    return render(request, 'cars/cars.html', {'vehicle_form': form, 'uuid': uuid})

def waiver_render(request, uuid):
    if request.method == 'POST':
        form = forms.WaiverForm(request.POST)
        if form.is_valid():
                #Add the waiver into the database for the given person
            form.create(uuid)
    else:
        form = forms.WaiverForm()
    return render(request, 'waivers/waivers.html', {'waiver_form': form, 'uuid': uuid})


def signup_render(request):
    if request.method == 'POST':
        form = forms.SignupForm(request.POST, request.FILES)
        if form.is_valid():
            #TODO What do we need to do about password validation?
            if form.verify_password():
                try:
                    form.create_user()
                except Exception:
                    messages.error(request, "System failed to create user; please try again.")
                else:
                    #Send user back to login page to login
                    return HttpResponseRedirect('/')
            else:
                messages.error(request, "Passwords were not equal; please try again.")
        else:
            messages.error(request, "User input was malformed or failed a test")
    else:
        form = forms.SignupForm()
    return render(request, 'signup/index.html', {'form': form})

def manage_ti_render(request, uuid):
    #Here we just supply the shit and defer aciton to mange_ti_delete and manage_ti_add
    add_form = forms.NameForm()
    delete_form = forms.NameForm()
    return render(request, 'ti/index.html', {'add_form': add_form, 'delete_form': delete_form, 'uuid': uuid})

def manage_ti_delete(request, uuid):
    if request.method == 'POST':
        delete_form = forms.NameForm(request.POST)
        if not delete_form.is_valid():
            if not delete_form.delete():
                messages.error(request, "Username doesn't exist or the write failed otherwise.")
            else:
                messages.success(request, "Tech Inspector DELETED")
    add_form = forms.NameForm()
    delete_form = forms.NameForm()
    return render(request, 'ti/index.html', {'add_form': add_form, 'delete_form': delete_form, 'uuid': uuid})

def manage_ti_add(request, uuid):
    if request.method == 'POST':
        add_form = forms.NameForm(request.POST)
        if add_form.is_valid():
            if not add_form.add():
                messages.error(request, "Username doesn't exist or the write failed otherwise.")
            else:
                messages.success(request, "Tech Inspector ADDED")

    add_form = forms.NameForm()
    delete_form = forms.NameForm()
    return render(request, 'ti/index.html', {'add_form': add_form, 'delete_form': delete_form, 'uuid': uuid})

def review_render(request, uuid):
    #We're going to use the same delegation strategy to handle this stuff.
    #Since this page really only asks for a name, that's all we include to start.
    name_form = forms.NameForm()
    return render(request, 'ti/review.html', {'name_form': name_form, 'uuid': uuid})

def review_get_cars(request, uuid):
    if request.method == 'POST':
        name_form = forms.NameForm(request.POST)
        if name_form.is_valid():
            cars = name_form.get_cars()
            if len(cars) == 0:
                messages.error(request, "Search failed for cars for this user.")
                return render(request, 'ti/review.html', {'name_form': name_form, 'uuid': uuid})
            else:
                vehicle_choice_form = forms.VehicleChoiceForm()
                vehicle_choice_form.set_queryset(cars)
        else:
            messages.error(request, "Information sent was rejected by validation test.")

    return render(request, 'ti/review.html', {'name_form': name_form, 'vehicle_choice_form': vehicle_choice_form, 'uuid': uuid})



def review_get_inspection(request, uuid):
    if request.method == 'POST':
        vehicle_choice = forms.VehicleChoiceForm(request.POST)
        if vehicle_choice.is_valid():
            #Get the inspection and return it.
            print(type(vehicle_choice.cleaned_data['UserVehicle']))
            insp = vehicle_choice.cleaned_data['UserVehicle'].inspectionID
            insp_fm = forms.InspectionForm(instance=insp)
            insp_fm.set_UserVehicle(vehicle_choice.cleaned_data['UserVehicle'])
            insp_fm.set_inspectionID(insp.inspectionID)
            #define name_form, repass vehicle_choice, repass uuid, create inspection form
            name_form = forms.NameForm()
            name_form.fields['username'] = vehicle_choice.cleaned_data['UserVehicle'].UUID.username

            return render(request, 'ti/review.html', {'name_form': name_form, 'vehicle_choice_form': vehicle_choice, 'inspection_form': insp_fm, 'uuid': uuid})
        else:
            name_form = forms.NameForm()
            messages.error(request, "Information sent was rejected by validation test.")
            return render(request, 'ti/review.html', {'name_form': name_form, 'uuid': uuid})
    else:
        name_form = forms.NameForm()

    return render(request, 'ti/review.html', {'name_form': name_form, 'uuid': uuid})



