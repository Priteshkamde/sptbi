from .forms import UserForm
from django.contrib.auth import authenticate, login, logout
from .models import Student
from hire.models import Company, JobPost, Applications
from django.shortcuts import render, get_list_or_404, get_object_or_404, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.contrib.auth.models import User


def index(request):
    jobs = JobPost.objects.all()
    if request.user_agent.is_mobile:
        return render(request, 'apply/index_mobile.html', {'jobs': jobs})
    else:
        return render(request, 'apply/index.html', {'jobs': jobs})


def detail(request, pk):
    job = get_object_or_404(JobPost, pk=pk)
    if request.user.is_authenticated and Student.objects.filter(user=request.user).exists():
        isStudent = True
        if Applications.objects.filter(post=job).exists():
            for applicant in Applications.objects.filter(post=job):
                if applicant.student == Student.objects.filter(user=request.user)[0]:
                    hasApplied = True
                    break
            else:
                hasApplied = False
        else:
            hasApplied = False
    else:
        isStudent = False
        hasApplied = False

    if request.method == 'POST':
        application = Applications()
        application.student = Student.objects.filter(user=request.user)[0]
        application.post = job
        application.save()
        return redirect('apply:detail', job.id)
    if request.user_agent.is_mobile:
        return render(request, 'apply/detail_mobile.html',
                      {'job': job, 'isStudent': isStudent, 'hasApplied': hasApplied})
    else:
        return render(request, 'apply/detail.html', {'job': job, 'isStudent': isStudent, 'hasApplied': hasApplied})


def profile(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if not request.user.is_authenticated:
        return login_user(request)
    elif student.user != request.user:
        isSelf = False
    else:
        isSelf = True
    applications = Applications.objects.filter(student=student)
    return render(request, 'apply/profile.html', {'student': student, 'applications': applications, 'isSelf': isSelf})


def login_user(request):
    if request.user.is_authenticated and Student.objects.filter(user=request.user).exists():
        return redirect('apply:index')
    if request.method == "POST":
        username = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None and Student.objects.filter(user=user).exists():
            if user.is_active:
                login(request, user)
                return redirect('apply:index')
            else:
                return render(request, 'apply/login.html', {'error_message': 'Your account is not active.'})
        else:
            return render(request, 'apply/login.html', {'error_message': 'Invalid login'})
    return render(request, 'apply/login.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')


def register_user(request):
    if request.user.is_authenticated and Student.objects.filter(user=request.user).exists():
        return redirect('apply:index')
    user_form = UserForm(request.POST or None)
    if user_form.is_valid():
        user = user_form.save(commit=False)
        email = user_form.cleaned_data['username']
        user.email = email
        password = user_form.cleaned_data['password']
        user.set_password(password)
        user.is_active = False
        user.save()

        student = Student()
        student.user = user
        student.phone_number = request.POST['phone_number']
        student.current_city = request.POST['current_city']
        student.interests = request.POST['interests']
        student.address = request.POST['address']
        student.qualification = request.POST['qualification']
        student.photo = request.FILES.get('photo', False)
        student.resume = request.FILES.get('resume', False)
        student.save()

        current_site = get_current_site(request)
        mail_subject = 'Activate your blog account.'
        message = render_to_string('apply/acc_active_email.html', {
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
        return HttpResponse('Please confirm your email address to complete the registration')

        '''user = authenticate(username=email, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if "next" in request.POST:
                    return redirect(request.POST.get("next"))
                else:
                    jobs = JobPost.objects.all()
                    if request.user_agent.is_mobile:
                        return render(request, 'apply/index_mobile.html', {'jobs': jobs})
                    else:
                        return render(request, 'apply/index.html', {'jobs': jobs})'''
    context = {
        "form": user_form,
    }
    return render(request, 'apply/register.html', context)


def logout_user(request):
    logout(request)
    return redirect('apply:login_user')
