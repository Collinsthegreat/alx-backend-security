import logging
import requests
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from .models import RequestLog, BlockedIP

logger = logging.getLogger(__name__)


class RequestLogMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip = self.get_client_ip(request)

        # 🔒 Blocked IP check
        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden("Your IP is blocked.")

        # 🌍 Check cache for geolocation
        geo_data = cache.get(ip)
        if not geo_data:
            try:
                response = requests.get(f"http://ip-api.com/json/{ip}").json()
                geo_data = {
                    "country": response.get("country"),
                    "city": response.get("city"),
                }
                cache.set(ip, geo_data, 60 * 60 * 24)  # Cache for 24h
            except Exception as e:
                logger.error(f"Geolocation lookup failed for {ip}: {e}")
                geo_data = {"country": None, "city": None}

        # 📝 Log request
        try:
            RequestLog.objects.create(
                ip_address=ip,
                path=request.path,
                country=geo_data["country"],
                city=geo_data["city"],
            )
        except Exception:
            logger.exception("Failed to log request")

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "")
