from django import forms
from django.forms import ModelForm
from pages.models import Image, TIUser, Waiver, Vehicle, Inspection
from django.forms.widgets import TextInput, NumberInput
import datetime
from pages import utils

class LoginForm(forms.Form):
    #max_length matches max_length for username field in pages/models.TIUser
    username = forms.CharField(label="username", max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
class NameForm(forms.Form):
    username = forms.CharField(label="username", max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    def delete(self):
        if self.is_valid():
            try:
                user = TIUser.objects.get(username=self.cleaned_data['username'])
                if user:
                    user.isTI = False
                    user.save()
                    return True
                else:
                    print("Failed to save results after NameForm.delete()")
                    return False
            except Exception:
                return False
        return False

    def add(self):
        if self.is_valid():
            try: 
                user = TIUser.objects.get(username=self.cleaned_data['username'])
                if user:
                    user.isTI = True
                    user.save()
                    return True
                else:
                    print("Failed to save results after NameForm.add()")
                    return False
            except Exception:
                return False
        return False

class SignupForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    first_name= forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last name'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    confirm_pass = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Verify Password'}))
    image = forms.ImageField(required=False)
    def verify_password(self):
        if self.is_valid():
            passw = self.cleaned_data['password']
            conf_pass = self.cleaned_data['confirm_pass']
            if passw == conf_pass:
                return True
        return False
    def create_user(self):
        if self.verify_password() and self.is_valid():
            entry = TIUser.objects.create_user(username=self.cleaned_data['username'], email=self.cleaned_data['email'], password=self.cleaned_data['password'])
            entry.image = self.cleaned_data['image']
            entry.first_name= self.cleaned_data['first_name']
            entry.last_name = self.cleaned_data['last_name']
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
                'goodHelmet', 'isNoviceDriver',
                'optionalExteriorPhoto',
                'optionalInteriorPhoto', 'optionalHUTPhoto'
                ]
        widgets = {
                'goodBatteryandConnectionsNotes': TextInput(attrs={'placeholder': 'Notes'}),
                'goodAirIntakeandSecureNotes': TextInput(attrs={'placeholder': 'Notes'}),
                'goodThrottleCableNotes': TextInput(attrs={'placeholder': 'Notes'}),
                'goodFluidCapsNotes': TextInput(attrs={'placeholder': 'Notes'}),
                'noMajorLeaksNotes': TextInput(attrs={'placeholder': 'Notes'}),
                'emptyTrunkNotes': TextInput(attrs={'placeholder': 'Notes'}),
                'functionalExhaustNotes': TextInput(attrs={'placeholder': 'Notes'}),
                }
    def __init__(self, uuid, *args, **kwargs):
        super(InspectionForm, self).__init__(*args, **kwargs)
        #Must set the queryset(aka the list of values to be shown) for UserVehicle to the actual cars of the user
        self.fields['UserVehicle'].queryset = Vehicle.objects.filter(UUID=utils.get_user(uuid))
        self.fields['goodBatteryandConnectionsNotes'].required = False
        self.fields['goodAirIntakeandSecureNotes'].required = False
        self.fields['goodThrottleCableNotes'].required = False
        self.fields['goodFluidCapsNotes'].required = False
        self.fields['noMajorLeaksNotes'].required = False
        self.fields['emptyTrunkNotes'].required = False
        self.fields['functionalExhaustNotes'].required = False
        self.fields['optionalExteriorPhoto'].required = False
        self.fields['optionalInteriorPhoto'].required = False
        self.fields['optionalHUTPhoto'].required = False
    def create(self):
        try:
            if self.is_valid():
                inspection = self.save(commit=False)
                inspection.UserVehicle.inspectionID = inspection
                inspection.save()
                inspection.UserVehicle.save()
        except Exception:
            print("Something didn't work in InspectionForm.create(); bad save?")
        return None

class VehicleForm(ModelForm):
    class Meta:
        model = Vehicle
        fields = ['name','VIN', 'vehicleYear', 'vehicleMake', 'vehicleModel', 'vehicleType', 'vehicleAvatar']
        widgets = {
                'name': TextInput(attrs={'placeholder': 'Car nickname'}),
                'VIN': TextInput(attrs={'placeholder': 'Car VIN'}),
                'vehicleYear': NumberInput(attrs={'placeholder': 'Year made', 'min': 1920, 'max': datetime.datetime.now().year + 1}),
                'vehicleMake': TextInput(attrs={'placeholder': 'Vehicle Make'}),
                'vehicleModel': TextInput(attrs={'placeholder': 'Vehicle Model'}),
                }
    def __init__(self, *args, **kwargs):
        super(VehicleForm, self).__init__(*args, **kwargs)
        self.fields['vehicleType'].initial = 'Vehicle Type'
        self.fields['vehicleAvatar'].required = False
    def create(self, uuid):
        if self.is_valid():
            print("We aren't getting here at all in VehicleForm/create")
            entry = Vehicle(name=self.cleaned_data['name'], VIN=self.cleaned_data['VIN'], vehicleYear=self.cleaned_data['vehicleYear'], vehicleMake = self.cleaned_data['vehicleMake'], vehicleModel=self.cleaned_data['vehicleModel'], vehicleType = self.cleaned_data['vehicleType'])
            entry.UUID = utils.user_list[uuid].user
            entry.vehicleAvatar = self.cleaned_data['vehicleAvatar']
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
        fields = ['username', 'email', 'image', 'first_name', 'last_name']
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['readonly'] = True
        self.fields['email'].widget.attrs['readonly'] = True
        self.fields['first_name'].widget.attrs['readonly'] = True
        self.fields['last_name'].widget.attrs['readonly'] = True

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
