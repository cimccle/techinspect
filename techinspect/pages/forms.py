from django import forms
from django.forms import ModelForm
from pages.models import Image, TIUser, Waiver, Vehicle, Inspection
from django.forms.widgets import TextInput, NumberInput
from datetime import datetime
from pages import utils

class LoginForm(forms.Form):
    #max_length matches max_length for username field in pages/models.TIUser
    username = forms.CharField(label="username", max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

class SignupForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    confirm_pass = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Verify Password'}))
    image = forms.ImageField(required=False)
    def verify_password(self):
        passw = self.cleaned_data['password']
        conf_pass = self.cleaned_data['confirm_pass']
        if passw != conf_pass:
            return False
        return True
    def create_user(self):
        if self.verify_password():
            entry = TIUser.objects.create_user(self.cleaned_data['username'], email=self.cleaned_data['email'], password=self.cleaned_data['password'])
            #user_image = Image(image=self.cleaned_data['image'])
            #key = user_image.imageID
            entry.image = self.cleaned_data['image']
            entry.save()
            return True and TIUser.objects.get(username=entry.username)
        return False
         

class ImageForm(ModelForm):
    class Meta:
        model = Image
        fields = ['image']

class WaiverForm(ModelForm):
    class Meta:
        model = Waiver
        fields = ['waiverDate', 'waiverName']
    #TODO maybe utilize first/last name in account creation so we can compare against the user input?
    def create(self, uuid):
        try:
            user = utils.get_user(uuid)
            if self.is_valid():
                waiver = Waiver(waiverDate=self.cleaned_data['waiverDate'], waiverName=self.cleaned_data['waiverName'])
                waiver.UUID = user
                waiver.save()
            else:
                #LOGGING?
                print("Creating the form failed")
        except Exception:
            print("Failed to find user")


class InspectionForm(ModelForm):
    class Meta:
        model = Inspection
        fields = ['UserVehicle','noWheelPlay', 'goodWheels', 'goodHubCaps', 'goodTires',
                'goodTireTreadDepth', 'goodBreakPads', 'noLooseBodyPanels',
                'goodNumbers', 'goodFloorMats', 'secureBTC', 'goodBreakPedal',
                'noExcessPlayinSteering', 'goodSeat', 'goodSeatBelt', 'goodMountedCamera',
                'goodBatteryandConnections', 'goodBatteryandConnectionsNotes',
                'goodAirIntakeandSecure', 'goodAirIntakeandSecureNotes',
                'goodThrottleCable', 'goodThrottleCableNotes',
                'goodFluidCaps', 'goodFluidCapsNotes',
                'noMajorLeaks', 'noMajorLeaksNotes',
                'emptyTrunk', 'emptyTrunkNotes',
                'functionalExhaust', 'functionalExhaustNotes',
                'goodHelmet', 'isNoviceDriver'
                ]

    def __init__(self, uuid, *args, **kwargs):
        super(InspectionForm, self).__init__(*args, **kwargs)
        #Must set the queryset(aka the list of values to be shown) for UserVehicle to the actual cars of the user
        self.fields['UserVehicle'].queryset = Vehicle.objects.filter(UUID=utils.get_user(uuid))
        #TODO Remove any undesireable entries(that already have up to date inspections)
        #for entry in self.fields['UserVehicle'].queryset
            #if entry.inspectionID
            #somehow remove the value from the queryset
    def create(self):
        try:
            if self.is_valid():
                self.save()
        except Exception:
            print("Something didn't work in InspectionForm.create(); bad save?")

class VehicleForm(ModelForm):
    class Meta:
        model = Vehicle
        fields = ['name','VIN', 'vehicleYear', 'vehicleMake', 'vehicleModel']
        widgets = {
                'name': TextInput(attrs={'placeholder': 'Car nickname'}),
                'VIN': TextInput(attrs={'placeholder': 'Car VIN'}),
                'vehicleYear': NumberInput(attrs={'placeholder': 'Year made', 'min': 1920, 'max': datetime.now().year + 1}),
                'vehicleMake': TextInput(attrs={'placeholder': 'Vehicle Make'}),
                'vehicleModel': TextInput(attrs={'placeholder': 'Vehicle Model'}),
                }
    def create(self, uuid):
        if self.is_valid():
            entry = Vehicle(VIN=self.cleaned_data['VIN'], vehicleYear=self.cleaned_data['vehicleYear'], vehicleMake = self.cleaned_data['vehicleMake'], vehicleModel=self.cleaned_data['vehicleModel'])
            entry.UUID = utils.user_list[uuid].user
            print(entry)
            entry.save()
    def read_only(self):
        self.fields['VIN'].widget.attrs['readonly'] = True
        self.fields['vehicleYear'].widget.attrs['readonly'] = True
        self.fields['vehicleMake'].widget.attrs['readonly'] = True
        self.fields['vehicleModel'].widget.attrs['readonly'] = True




class ProfileForm(ModelForm):
    class Meta:
        model = TIUser
        fields = ['username', 'email', 'image']
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['readonly'] = True
        self.fields['email'].widget.attrs['readonly'] = True
        self.fields['image'].widget.attrs['readonly'] = True

class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Current Password'}))
    old_confirm_pass = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Verify Current Password'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'New Password'}))
    confirm_pass = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Verify New Password'}))
    def verify_old_password(self, uuid):
        user = utils.get_user(uuid)
        if self.cleaned_data['old_password'] == self.cleaned_data['old_confirm_pass'] and user.check_password(self.cleaned_data['old_confirm_pass']):
            return True
        return False
    def verify_new_password(self):
        passw = self.cleaned_data['password']
        conf_pass = self.cleaned_data['confirm_pass']
        if passw != conf_pass:
            return False
        return True
