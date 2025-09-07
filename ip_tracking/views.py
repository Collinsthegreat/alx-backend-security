from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django_ratelimit.decorators import ratelimit

def home(request):
    return HttpResponse(
        "<h1>Welcome to ALX Backend Security Project 🚀</h1>"
        "<p>Use /admin/, /anon-login/, or /user-login/</p>"
    )

# Anonymous users: 5 requests/minute
@csrf_exempt
@ratelimit(key="ip", rate="5/m", method="POST", block=True)
def anon_login(request):   # 👈 renamed to match urls.py
    if request.method == "POST":
        return JsonResponse({"message": "Anonymous login attempt"})
    return JsonResponse({"error": "POST only"}, status=405)

# Authenticated users: 10 requests/minute
@csrf_exempt
@ratelimit(key="user", rate="10/m", method="POST", block=True)
def user_login(request):
    if request.user.is_authenticated:
        return JsonResponse({"message": f"User {request.user.username} login attempt"})
    return JsonResponse({"error": "Unauthorized"}, status=401)
