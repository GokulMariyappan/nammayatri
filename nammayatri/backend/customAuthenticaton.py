from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, get_backends
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
import json
from .models import CustomUser
from django.forms.models import model_to_dict

@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')
        
        if not (email and password and role and username):
            return JsonResponse({'error': 'Missing fields'}, status=400)
        
        user = CustomUser(email=email, password=password)
        user.role = role  # Assign role separately if it's a model field
        user.save()
        return JsonResponse({'message': 'User registered successfully'})

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        user = get_object_or_404(CustomUser,email = email) # Uses EmailAuthBackend
        print(email, password, authenticate(request, username = email, password = password), CustomUser.objects.all())
        if user:
            login(request, user)
            ruser = model_to_dict(user)
            return JsonResponse({'message': 'Login successful','user': ruser})
        
        return JsonResponse({'error': f'Invalid credentials {email} {password}'}, status=400)

@login_required
def logout_view(request):
    logout(request)
    return JsonResponse({'message': 'Logged out successfully'})