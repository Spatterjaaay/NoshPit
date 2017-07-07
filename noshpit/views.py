from django.shortcuts import render

def home(request):
    return render(request, 'noshpit/home.html', {})

def start_a_pit(request):
    return render(request, 'noshpit/start_a_pit.html', {})
    pass

def join_a_pit(request):
    return render(request, 'noshpit/join_a_pit.html', {})
    pass
