from django.db import models

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