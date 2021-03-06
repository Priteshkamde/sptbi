from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from .models import JobPost, Company


class UserForm(forms.ModelForm):
    username = forms.EmailField(required=True, label="Email",
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'password')


class JobPostForm(forms.ModelForm):
    job_title = forms.CharField(required=True, label="Title:",
                                widget=forms.TextInput(attrs={'class': 'form-control'}))

    job_type = forms.ChoiceField(required=True, label="Type",
                                 choices=(('Full Time', 'Full Time'), ('Part Time', 'Part Time')),
                                 widget=forms.Select(attrs={'class': 'form-control'}))

    salary = forms.CharField(required=True, label="Salary:",
                             widget=forms.TextInput(attrs={'class': 'form-control'}))

    intake = forms.IntegerField(required=True, label="Intake:",
                                widget=forms.NumberInput(attrs={'class': 'form-control'}))

    duration = forms.IntegerField(required=True, label="Duration:",
                                  widget=forms.NumberInput(attrs={'class': 'form-control'}))

    description = forms.CharField(required=True, label="Description:",
                                  widget=forms.Textarea(attrs={'class': 'form-control'}))

    other_requirements = forms.CharField(required=True, label="Other Requirements:",
                                         widget=forms.Textarea(attrs={'class': 'form-control'}))

    perks = forms.CharField(required=True, label="Perks::",
                            widget=forms.Textarea(attrs={'class': 'form-control'}))

    class Meta:
        model = JobPost
        fields = ('job_title', 'job_type', 'salary', 'intake', 'duration',
                  'description', 'other_requirements', 'perks')


class EditJobPostForm(UserChangeForm):
    job_title = forms.CharField(required=True, label="Title:",
                                widget=forms.TextInput(attrs={'class': 'form-control'}))

    job_type = forms.ChoiceField(required=True, label="Type",
                                 choices=(('Full Time', 'Full Time'), ('Part Time', 'Part Time')),
                                 widget=forms.Select(attrs={'class': 'form-control'}))

    salary = forms.CharField(required=True, label="Salary:",
                             widget=forms.TextInput(attrs={'class': 'form-control'}))

    intake = forms.IntegerField(required=True, label="Intake:",
                                widget=forms.NumberInput(attrs={'class': 'form-control'}))

    duration = forms.IntegerField(required=True, label="Duration:",
                                  widget=forms.NumberInput(attrs={'class': 'form-control'}))

    description = forms.CharField(required=True, label="Description:",
                                  widget=forms.Textarea(attrs={'class': 'form-control'}))

    other_requirements = forms.CharField(required=True, label="Other Requirements:",
                                         widget=forms.Textarea(attrs={'class': 'form-control'}))

    perks = forms.CharField(required=True, label="Perks::",
                            widget=forms.Textarea(attrs={'class': 'form-control'}))

    class Meta:
        model = JobPost
        fields = ('job_title', 'job_type', 'salary', 'intake', 'duration',
                  'description', 'other_requirements', 'perks')


class EditProfileForm(UserChangeForm):
    name = forms.CharField(label='Company Name:', widget=forms.TextInput, required=True)
    website = forms.URLField(label='Company Website:', widget=forms.TextInput, required=False)
    phone_number = forms.CharField(label='Contact No:', widget=forms.TextInput, required=True)
    logo = forms.ImageField(label="Company Logo:", required=False)
    description = forms.CharField(label='Company Description:', widget=forms.Textarea, required=True)

    class Meta:
        model = Company
        fields = ('name', 'website', 'phone_number', 'logo', 'description')
