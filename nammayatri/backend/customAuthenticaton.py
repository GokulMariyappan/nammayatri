from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
import json

User = get_user_model()

@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')
        
        if not (email and username and password and role):
            return JsonResponse({'error': 'Missing fields'}, status=400)
        
        user = User.objects.create_user(email=email, username=username, password=password, role=role)
        return JsonResponse({'message': 'User registered successfully'})

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        user = authenticate(request, username=email, password=password)  # Uses EmailAuthBackend
        
        if user:
            login(request, user)
            return JsonResponse({'message': 'Login successful'})
        
        return JsonResponse({'error': 'Invalid credentials'}, status=400)

@login_required
def logout_view(request):
    logout(request)
    return JsonResponse({'message': 'Logged out successfully'})