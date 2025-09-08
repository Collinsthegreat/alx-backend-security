# ip_tracking/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django_ratelimit.decorators import ratelimit

def home(request):
    # Keeping this as plain Django view (not for Swagger)
    return HttpResponse(
        "<h1>Welcome to ALX Backend Security Project 🚀</h1>"
        "<p>Use /admin/, /anon-login/, or /user-login/</p>"
    )

# Anonymous users: 5 requests/minute
@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
@ratelimit(key="ip", rate="5/m", method="POST", block=True)
def anon_login(request):
    return Response({"message": "Anonymous login attempt"})

# Authenticated users: 10 requests/minute
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@ratelimit(key="user", rate="10/m", method="POST", block=True)
def user_login(request):
    user = request.user
    return Response({"message": f"User {user.username} login attempt"})
