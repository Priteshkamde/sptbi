from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


def index(request):
    return render(request, 'home/index.html')


def change_password(request):
    if not request.user.is_authenticated:
        return redirect('home:index')
    if request.method == 'POST':
        form = PasswordChangeForm(request.user or None, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('home:change_password')
        else:
            return render(request, 'home/change_password.html', {'form': form, 'error_message': 'Invalid Input'})
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'home/change_password.html', {
        'form': form
    })

