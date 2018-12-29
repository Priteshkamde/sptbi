from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{10,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. "
                                         "Up to 15 digits allowed.")

    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    address = models.CharField(max_length=100)
    qualification = models.CharField(max_length=100)
    current_city = models.CharField(max_length=20)
    photo = models.ImageField(upload_to='media/photos', blank=True)
    resume = models.FileField(upload_to='media/resume', blank=True)
    interests = models.CharField(max_length=1000)
