from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from apply.models import Student


class UserForm(forms.ModelForm):
    first_name = forms.CharField(required=True,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.EmailField(required=True, label="Email",
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password')


class EditProfileForm(UserChangeForm):
    first_name = forms.CharField(label="First Name:", required=True)
    last_name = forms.CharField(label="Last Name", required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class EditStudentProfileForm(UserChangeForm):
    phone_number = forms.CharField(label="Contact No:", required=True)
    qualification = forms.CharField(label="Qualification", required=True)
    current_city = forms.CharField(label="City:", required=True)
    photo = forms.ImageField(label="Photo:", required=False)
    resume = forms.FileField(label="Resume:", required=True)
    address = forms.CharField(label="Address:", widget=forms.Textarea,required=True)

    class Meta:
        model = Student
        fields = ('phone_number', 'qualification', 'current_city', 'photo', 'resume', 'address')
