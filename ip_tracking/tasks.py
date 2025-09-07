# ip_tracking/tasks.py
from datetime import timedelta
from typing import Optional, Type

from celery import shared_task
from django.core.mail import send_mail
from django.apps import apps
from django.db.models import Count, Q
from django.utils import timezone

# Keep the list small and explicit to avoid noisy flags.
SENSITIVE_PATH_PREFIXES = ("/admin", "/login")


def _resolve_request_model() -> Optional[Type]:
    """Find a model that looks like a request log.
    Why: different starter repos use different names; this keeps the task portable.
    Expected fields: ip_address, path, created_at.
    """
    candidates = (
        ("ip_tracking", "RequestLog"),
        ("ip_tracking", "RequestEvent"),
        ("core", "RequestLog"),
        ("logs", "RequestLog"),
    )
    for app_label, model_name in candidates:
        try:
            model = apps.get_model(app_label, model_name)
        except Exception:
            continue
        # Best-effort field check to reduce runtime surprises.
        field_names = {f.name for f in model._meta.get_fields()}
        if {"ip_address", "path", "created_at"}.issubset(field_names):
            return model
    return None


@shared_task(bind=True, name="ip_tracking.flag_suspicious_ips")
def flag_suspicious_ips(self, request_limit: int = 100, window_minutes: int = 60) -> str:
    """Anomaly detection task: flags IPs with high volume or sensitive-path hits.
    Why bind=True: allows access to self.request.id for debugging in task monitors.
    """
    RequestModel = _resolve_request_model()
    if RequestModel is None:
        return (
            "No suitable request-log model found. Expected fields: ip_address, path, created_at."
        )

    SuspiciousIP = apps.get_model("ip_tracking", "SuspiciousIP")

    since = timezone.now() - timedelta(minutes=window_minutes)
    recent = RequestModel.objects.filter(created_at__gte=since)

    # 1) High-volume IPs (> request_limit in window)
    high_volume = (
        recent.values("ip_address")
        .annotate(total=Count("id"))
        .filter(total__gt=request_limit)
    )

    created_hv = 0
    for row in high_volume:
        reason = f">{request_limit} requests in last {window_minutes}m ({row['total']})"
        _, created = SuspiciousIP.objects.get_or_create(
            ip_address=row["ip_address"], reason=reason
        )
        created_hv += int(created)

    # 2) Sensitive path access (prefix match)
    q = Q()
    for prefix in SENSITIVE_PATH_PREFIXES:
        q |= Q(path__startswith=prefix)

    sensitive_ips = recent.filter(q).values("ip_address").distinct()

    created_sp = 0
    for row in sensitive_ips:
        _, created = SuspiciousIP.objects.get_or_create(
            ip_address=row["ip_address"], reason="accessed sensitive path"
        )
        created_sp += int(created)

    return f"created: high_volume={created_hv}, sensitive={created_sp}"

@shared_task
def send_test_email(to_email):
    send_mail("Render Celery Test", "This is a test", "no-reply@example.com", [to_email])
    return "sent"
