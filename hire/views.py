from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserForm, JobPostForm, EditProfileForm, EditJobPostForm
from django.contrib.auth import authenticate, login, logout
from .models import Company, JobPost, Applications, JobCategory, Message
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
import time


def post_job(request):
    if not request.user.is_authenticated or not Company.objects.filter(user=request.user).exists():
        return login_user(request)
    form = JobPostForm(request.POST or None)
    if form.is_valid():
        job_post = form.save(commit=False)
        job_post.company = Company.objects.filter(user=request.user)[0]
        job_post.save()
        categories = str(request.POST['job_category']).lower().split(",")
        for category in categories:
            if JobCategory.objects.filter(job_category=category).exists():
                j = JobCategory.objects.filter(job_category=category)[0]
            else:
                j = JobCategory(job_category=category)
                j.save()
            j.job_post.add(job_post)
            j.save()
        return redirect('hire:index')
    return render(request, 'hire/post.html', {'form': form})


def index(request):
    if not request.user.is_authenticated or not Company.objects.filter(user=request.user).exists():
        return redirect('hire:login_user')
    applications = list()
    company = Company.objects.filter(user=request.user)[0]
    jobs = JobPost.objects.filter(company=company)
    messages = Message.objects.all()

    if request.method == "POST":
        message = Message()
        message.application = Applications.objects.filter(pk=request.POST.get('id'))[0]
        message.sender = request.user
        message.message = request.POST.get('message')
        message.datetime = str(time.asctime(time.localtime(time.time())))
        message.save()

    for job in jobs:
        applications.append(Applications.objects.filter(post=job))
    return render(request, 'hire/index.html', {'company': company, 'jobs': jobs, 'applications': applications,
                                               'messages': messages})


def shortlist(request, app_id):
    application = get_object_or_404(Applications, pk=app_id)
    if application.is_shortlisted:
        application.is_shortlisted = False
    else:
        application.is_shortlisted = True
    application.save()
    return redirect('hire:index')


def login_user(request):
    if request.user.is_authenticated and Company.objects.filter(user=request.user).exists():
        return redirect('hire:index')
    if request.method == "POST":
        username = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None and Company.objects.filter(user=user).exists():
            if user.is_active:
                login(request, user)
                return redirect('hire:index')
            else:
                return render(request, 'hire/login.html', {'error_message': 'Your account is not active.'})
        else:
            return render(request, 'hire/login.html', {'error_message': 'Invalid login'})
    return render(request, 'hire/login.html')


def verify_email(request, pk, slug):
    try:
        email = force_text(urlsafe_base64_decode(slug))
        user = User.objects.get(pk=pk)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        email = None

    if user.is_active:
        if user.is_authenticated:
            return redirect('hire:index')
        else:
            return redirect('hire:login_user')

    if request.method == "POST":
        if request.POST['confirm']:
            current_site = get_current_site(request)
            mail_subject = 'Activate your SPTBI account.'
            message = render_to_string('hire/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            email_message = EmailMessage(
                mail_subject, message, to=[email]
            )
            email_message.content_subtype = "html"
            email_message.send()
            return render(request, 'hire/confirm_acc.html', {'user': user})
    return render(request, 'hire/confirm_acc.html', {'user': user})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(User, pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user.is_active:
        if user.is_authenticated:
            return redirect('hire:index')
        else:
            return redirect('hire:login_user')

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return render(request, 'hire/confirm_success.html')
    else:
        return render(request, 'hire/confirm_success.html', {'error_message': 'Invalid verification link'})


def register_user(request):
    if request.user.is_authenticated and Company.objects.filter(user=request.user).exists():
        return redirect('hire:index')
    user_form = UserForm(request.POST or None)
    if user_form.is_valid():
        user = user_form.save(commit=False)
        email = user_form.cleaned_data['username']
        user.email = email
        password = user_form.cleaned_data['password']
        user.set_password(password)
        user.first_name = request.POST['company_name']
        user.is_active = False
        user.save()

        company = Company()
        company.user = user
        company.name = request.POST['company_name']
        company.website = request.POST['website']
        company.phone_number = request.POST['phone_number']
        company.description = request.POST['description']
        company.logo = request.FILES.get('logo', False)
        company.save()

        current_site = get_current_site(request)
        mail_subject = 'Activate your SPTBI account.'
        message = render_to_string('hire/acc_active_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
            'token': account_activation_token.make_token(user),
        })
        email_message = EmailMessage(
            mail_subject, message, to=[email]
        )
        email_message.content_subtype = "html"
        email_message.send()
        return redirect('hire:verify', user.pk, urlsafe_base64_encode(force_bytes(email)).decode())

    context = {
        "form": user_form,
    }
    return render(request, 'hire/register.html', context)


def logout_user(request):
    logout(request)
    return redirect('hire:login_user')


def delete_post(request, pk):
    JobPost.objects.filter(pk=pk).delete()
    return redirect('hire:index')


def edit_post(request, pk):
    post = get_object_or_404(JobPost, pk=pk)
    if request.user.is_authenticated and Company.objects.filter(user=request.user).exists():
        company = Company.objects.filter(user=request.user)[0]
        if not(post.company == company):
            return redirect('hire:index')
        else:
            categories = JobCategory.objects.filter(job_post=post)
            form = EditJobPostForm(request.POST or None, instance=post)

            if form.is_valid():
                form.save()
                for category in categories:
                    category.job_post.remove(post)
                    category.save()

                new_categories = str(request.POST['job_category']).lower().split(",")
                for new_category in new_categories:
                    if JobCategory.objects.filter(job_category=new_category).exists():
                        j = JobCategory.objects.filter(job_category=new_category)[0]
                    else:
                        j = JobCategory(job_category=new_category)
                        j.save()
                    j.job_post.add(post)
                    j.save()

                return redirect('hire:index')
            return render(request, 'hire/edit_post_form.html', {'form': form, 'categories': categories})
    else:
        return redirect('hire:login_user')


def edit_profile(request):
    if request.user.is_authenticated and Company.objects.filter(user=request.user).exists():
        company = Company.objects.filter(user=request.user)[0]
        form = EditProfileForm(request.POST or None, instance=Company.objects.filter(user=request.user)[0])

        if form.is_valid():
            company.logo = request.FILES.get('logo')
            company.save()
            form.save()
            return redirect('hire:index')
        return render(request, 'hire/edit_user_form.html', {'form': form})
    else:
        return redirect('hire:login_user')
