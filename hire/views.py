from django.shortcuts import render, redirect
from .forms import UserForm, JobPostForm
from django.contrib.auth import authenticate, login, logout
from .models import Company, JobPost, Applications


def post_job(request):
    if not request.user.is_authenticated or not Company.objects.filter(user=request.user).exists():
        return login_user(request)
    form = JobPostForm(request.POST or None)
    if form.is_valid():
        job_post = form.save(commit=False)
        job_post.company = Company.objects.filter(user=request.user)[0]
        job_post.save()
        form = JobPostForm()
        return redirect('hire:index')
    return render(request, 'hire/post.html', {'form': form})


def index(request):
    if not request.user.is_authenticated or not Company.objects.filter(user=request.user).exists():
        return redirect('hire:login_user')
    applications = list()
    company = Company.objects.filter(user=request.user)[0]
    jobs = JobPost.objects.filter(company=company)
    for job in jobs:
        applications.append(Applications.objects.filter(post=job))
    return render(request, 'hire/index.html', {'company': company, 'jobs': jobs, 'applications': applications})


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
        user.save()

        company = Company()
        company.user = user
        company.name = request.POST['company_name']
        company.phone_number = request.POST['phone_number']
        company.description = request.POST['description']
        company.save()

        user = authenticate(username=email, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                applications = list()
                company = Company.objects.filter(user=request.user)[0]
                return redirect('hire:index')
    context = {
        "form": user_form,
    }
    return render(request, 'hire/register.html', context)


def logout_user(request):
    logout(request)
    return redirect('hire:login_user')

