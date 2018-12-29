from django.shortcuts import render


def index(request):
    if request.user_agent.is_mobile:
        print("a")
    else:
        print("b")
    return render(request, 'home/index.html')
