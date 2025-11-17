from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomLoginForm

def registro(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Registro exitoso! Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registro.html', {'form': form})

def login(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            # Autenticar y obtener el usuario
            user = form.get_user()
            # Iniciar sesión
            auth_login(request, user)
            messages.success(request, f'¡Bienvenido, {user.username}!')
            return redirect('index')
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})

def logout(request):
    auth_logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')