from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from apply.models import Student


class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{10,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. "
                                         "Up to 15 digits allowed.")

    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=False)
    description = models.CharField(max_length=10000)
    website = models.URLField(max_length=128)
    logo = models.ImageField(upload_to='media/photos/hire', blank=True)

    def __str__(self):
        return self.name


class JobPost(models.Model):
    job_title = models.CharField(max_length=100)
    job_type = models.CharField(max_length=100, choices=(('Full Time', 'Full Time'), ('Part Time', 'Part Time')))
    salary = models.CharField(max_length=100)
    intake = models.IntegerField()
    duration = models.IntegerField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    description = models.CharField(max_length=10000)
    other_requirements = models.CharField(max_length=10000)
    perks = models.CharField(max_length=10000)


class JobCategory(models.Model):
    job_category = models.CharField(max_length=100)
    job_post = models.ManyToManyField(JobPost)


class Applications(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    post = models.ForeignKey(JobPost, on_delete=models.CASCADE)
    is_shortlisted = models.BooleanField(default=False)

    def __str__(self):
        return self.student.user.first_name + " " + self.student.user.last_name


class Message(models.Model):
    application = models.ForeignKey(Applications, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.CharField(max_length=100)
    message = models.CharField(max_length=50000)
