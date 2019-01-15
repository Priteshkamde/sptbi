import time

from django.http import HttpResponseRedirect
from .forms import UserForm, EditProfileForm, EditStudentProfileForm
from django.contrib.auth import authenticate, login, logout
from .models import Student, Interests
from hire.models import JobPost, Applications, JobCategory, Message
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from .filters import JobFilter


def index(request):
    jobs = JobPost.objects.all()
    job_filter = JobFilter(request.POST, queryset=jobs)
    job_category = request.POST.get('category')
    categories = JobCategory.objects.none()
    for job in job_filter.qs:
        categories |= JobCategory.objects.filter(job_post=job)

    categories = categories.distinct()
    job_list = list()
    if job_category is not None:
        for category in categories:
            if category.job_category in job_category.lower():
                for job in category.job_post.all():
                    if job not in job_list:
                        job_list.append(job)

        if request.user_agent.is_mobile:
            return render(request, 'apply/index_mobile.html',
                          {'jobs': jobs, 'filters': job_filter, 'categories': categories, 'job_list': job_list,
                           'job_category': job_category})
        else:
            return render(request, 'apply/index.html',
                          {'jobs': jobs, 'filters': job_filter, 'categories': categories, 'job_list': job_list,
                           'job_category': job_category})

    if request.user_agent.is_mobile:
        return render(request, 'apply/index_mobile.html',
                      {'jobs': jobs, 'filters': job_filter, 'categories': categories})
    else:
        return render(request, 'apply/index.html', {'jobs': jobs, 'filters': job_filter, 'categories': categories})


def detail(request, pk):
    job = get_object_or_404(JobPost, pk=pk)
    category = JobCategory.objects.filter(job_post=job)
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
                      {'job': job, 'isStudent': isStudent, 'hasApplied': hasApplied, 'categories': category})
    else:
        return render(request, 'apply/detail.html',
                      {'job': job, 'isStudent': isStudent, 'hasApplied': hasApplied, 'categories': category})


def profile(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if not request.user.is_authenticated:
        return redirect('apply:login')
    elif student.user != request.user:
        isSelf = False
    else:
        isSelf = True
    interests = Interests.objects.filter(student=student)
    applications = Applications.objects.filter(student=student)
    messages = Message.objects.all()

    if request.method == "POST":
        message = Message()
        message.application = Applications.objects.filter(pk=request.POST.get('id'))[0]
        message.sender = request.user
        message.message = request.POST.get('message')
        message.datetime = str(time.asctime(time.localtime(time.time())))
        message.save()

    return render(request, 'apply/profile.html',
                  {'student': student, 'applications': applications, 'isSelf': isSelf, 'interests': interests,
                   'messages': messages})


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
                if request.POST.get('next'):
                    return HttpResponseRedirect(request.POST.get('next', '/'))
                return redirect('apply:index')
            else:
                return render(request, 'apply/login.html', {'error_message': 'Your account is not active.'})
        else:
            return render(request, 'apply/login.html', {'error_message': 'Invalid login'})
    return render(request, 'apply/login.html')


def verify_email(request, pk, slug):
    try:
        email = force_text(urlsafe_base64_decode(slug))
        user = User.objects.get(pk=pk)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        email = None

    if user.is_active:
        return redirect('apply:index')

    if request.method == "POST":
        if request.POST['confirm'] == "resend":
            current_site = get_current_site(request)
            mail_subject = 'Activate your SPTBI account.'
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
            return render(request, 'apply/confirm_acc.html', {'user': user})
        elif request.POST['confirm'] == "continue":
            if user.is_active:
                login(request, user)
                return redirect('apply:index')
            else:
                return render(request, 'apply/confirm_acc.html',
                              {'user': user,
                               'error_message':
                                   "Your account is not yet verified. Did you click on the link you received on your email? Didn't recieve an email? Try resend email."
                               })

    return render(request, 'apply/confirm_acc.html', {'user': user})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(User, pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user.is_active:
        return redirect('apply:index')

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'apply/confirm_success.html')
    else:
        return render(request, 'apply/confirm_success.html', {'error_message': 'Invalid verification link'})


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
        student.address = request.POST['address']
        student.qualification = request.POST['qualification']
        student.photo = request.FILES.get('photo', False)
        student.resume = request.FILES.get('resume', False)
        student.save()

        interests = str(request.POST['interests']).split(",")
        for interest in interests:
            if Interests.objects.filter(interest=interest).exists():
                i = Interests.objects.filter(interest=interest)[0]
            else:
                i = Interests(interest=interest)
                i.save()
            i.student.add(student)
            i.save()

        current_site = get_current_site(request)
        mail_subject = 'Activate your SPTBI account.'
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
        return redirect('apply:verify', user.pk, urlsafe_base64_encode(force_bytes(email)).decode())

    context = {
        "form": user_form,
    }
    return render(request, 'apply/register.html', context)


def logout_user(request):
    logout(request)
    return redirect('apply:login_user')


def edit_profile(request):
    if request.user.is_authenticated and Student.objects.filter(user=request.user).exists():
        student = Student.objects.filter(user=request.user)[0]
        student_form = EditStudentProfileForm(request.POST or None,
                                              instance=student)
        user_form = EditProfileForm(request.POST or None, instance=request.user)
        interests = Interests.objects.filter(student=student)

        if student_form.is_valid() and user_form.is_valid():
            if student.photo:
                student.photo.delete()
            student.photo = request.FILES.get('photo', False)
            student.save()
            student_form.save()
            user_form.save()
            for interest in interests:
                interest.student.remove(student)
                interest.save()

            new_interests = str(request.POST['interests']).split(",")
            for new_interest in new_interests:
                if Interests.objects.filter(interest=new_interest).exists():
                    i = Interests.objects.filter(interest=new_interest)[0]
                else:
                    i = Interests(interest=new_interest)
                    i.save()
                i.student.add(student)
                i.save()
            return redirect('apply:profile', Student.objects.filter(user=request.user)[0].id)
        return render(request, 'apply/edit_profile.html',
                      {'user_form': user_form, 'form': student_form, 'interests': interests})
    else:
        return redirect('apply:login_user')
