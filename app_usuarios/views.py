from django.forms import Widget
from django.shortcuts import render, redirect
from .forms import *

# Create your views here.
def registro(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registro.html', {'form': form})

"""def login(request):
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            return redirect('home')
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})"""

"""def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})"""