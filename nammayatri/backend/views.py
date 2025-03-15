from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import View
from .models import CustomUser
from django.shortcuts import get_object_or_404
# Create your views here.

class HomeView(View):
    def get(self, request):
        return HttpResponse("This works for now")
    
class GetEmail(View):
    def get(self, request, email):
        print('im printing',email)
        user = get_object_or_404(CustomUser, email = email)
        r = {'role' : user.role}
        return JsonResponse(r)
