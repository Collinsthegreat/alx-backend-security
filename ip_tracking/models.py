''' from django.db import models

# Create your models here.
class RequestLog(models.Model):
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    path = models.CharField(max_length=2048)
    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.ip_address} {self.path} @ {self.timestamp}"

class BlockedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)

    def __str__(self):
        return self.ip_address
    

class SuspiciousIP(models.Model):

    ip_address = models.GenericIPAddressField(db_index=True)
    reason = models.CharField(max_length=255)


class Meta:
    indexes = [
    models.Index(fields=["ip_address"]),
]
# Prevents duplicate rows for the same reason on the same IP.
    constraints = [
    models.UniqueConstraint(
    fields=["ip_address", "reason"], name="uniq_suspicious_ip_reason"
)
]


    def __str__(self) -> str: # pragma: no cover (repr helper)
        return f"{self.ip_address} – {self.reason}"

'''

# ip_tracking/models.py
from datetime import timedelta
import logging
import requests

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Count
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


logger = logging.getLogger(__name__)


class RequestLog(models.Model):
    """
    Logs details about each incoming request for auditing and analytics.
    Includes geolocation data (via IP lookup) and metadata such as method/user-agent.
    """

    ip_address = models.GenericIPAddressField()
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    user_agent = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Request Log"
        verbose_name_plural = "Request Logs"
        indexes = [
            models.Index(fields=["ip_address"]),
            models.Index(fields=["country", "city"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return f"{self.ip_address} - {self.path} - {self.timestamp}"

    @classmethod
    def get_geolocation_data(cls, ip_address: str) -> dict:
        """
        Fetch geolocation data for an IP address (cached for 24h).
        Uses ip-api.com (free tier).
        """
        cache_key = f"ip_geo_{ip_address}"
        geo_data = cache.get(cache_key)

        if geo_data is None:
            try:
                response = requests.get(
                    f"http://ip-api.com/json/{ip_address}?fields=status,message,country,city,lat,lon",
                    timeout=5
                )
                data = response.json()

                if data.get("status") == "success":
                    geo_data = {
                        "country": data.get("country"),
                        "city": data.get("city"),
                        "latitude": data.get("lat"),
                        "longitude": data.get("lon"),
                    }
                    cache.set(cache_key, geo_data, 60 * 60 * 24)  # 24h cache
                else:
                    geo_data = {}
            except Exception as e:
                logger.error(f"Failed to get geolocation for {ip_address}: {str(e)}")
                geo_data = {}

        return geo_data


class BlockedIP(models.Model):
    """
    Stores blacklisted IP addresses that are forbidden from accessing the app.
    """

    ip_address = models.GenericIPAddressField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True, null=True, help_text="Reason for blocking this IP")
    is_active = models.BooleanField(default=True, help_text="Whether this IP block is active")

    class Meta:
        verbose_name = "Blocked IP"
        verbose_name_plural = "Blocked IPs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.ip_address} (Blocked at: {self.created_at})"

    def save(self, *args, **kwargs):
        try:
            self.full_clean()
        except ValidationError as e:
            raise ValidationError(_(f"Invalid IP address: {self.ip_address}")) from e
        super().save(*args, **kwargs)


class SuspiciousIPManager(models.Manager):
    def detect_suspicious_activity(self):
        """
        Detects suspicious IPs based on request patterns:
        - High request volume (>100/hour).
        - Accessing sensitive paths (from settings.SENSITIVE_PATHS).
        """

        from ip_tracking.models import RequestLog  # Local import to avoid circular imports
        one_hour_ago = timezone.now() - timedelta(hours=1)

        # High request volume detection
        high_volume_ips = (
            RequestLog.objects.filter(timestamp__gte=one_hour_ago)
            .values("ip_address")
            .annotate(request_count=Count("id"))
            .filter(request_count__gt=100)
            .values_list("ip_address", flat=True)
        )

        for ip in high_volume_ips:
            self.update_or_create(
                ip_address=ip,
                defaults={
                    "reason": SuspiciousIP.SuspicionReason.HIGH_REQUEST_VOLUME,
                    "details": {
                        "request_count": RequestLog.objects.filter(
                            ip_address=ip, timestamp__gte=one_hour_ago
                        ).count()
                    },
                    "is_active": True,
                },
            )

        # Sensitive paths detection
        sensitive_paths = getattr(settings, "SENSITIVE_PATHS", ["/admin/", "/login/"])
        suspicious_path_ips = (
            RequestLog.objects.filter(timestamp__gte=one_hour_ago, path__in=sensitive_paths)
            .values_list("ip_address", flat=True)
            .distinct()
        )

        for ip in suspicious_path_ips:
            self.update_or_create(
                ip_address=ip,
                defaults={
                    "reason": SuspiciousIP.SuspicionReason.SENSITIVE_PATH,
                    "details": {
                        "paths_accessed": list(
                            RequestLog.objects.filter(
                                ip_address=ip,
                                timestamp__gte=one_hour_ago,
                                path__in=sensitive_paths,
                            )
                            .values_list("path", flat=True)
                            .distinct()
                        )
                    },
                    "is_active": True,
                },
            )

        return self.filter(is_active=True).count()


class SuspiciousIP(models.Model):
    """
    Stores IPs flagged as suspicious by anomaly detection.
    """

    class SuspicionReason(models.TextChoices):
        HIGH_REQUEST_VOLUME = "high_volume", "High request volume"
        SENSITIVE_PATH = "sensitive_path", "Accessed sensitive path"
        MULTIPLE_VIOLATIONS = "multiple", "Multiple violations"

    ip_address = models.GenericIPAddressField(unique=True)
    reason = models.CharField(max_length=20, choices=SuspicionReason.choices)
    first_detected = models.DateTimeField(auto_now_add=True)
    last_detected = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    details = models.JSONField(default=dict, blank=True)

    objects = SuspiciousIPManager()

    class Meta:
        verbose_name = "Suspicious IP"
        verbose_name_plural = "Suspicious IPs"
        ordering = ["-last_detected"]

    def __str__(self):
        return f"{self.ip_address} - {self.get_reason_display()}"
