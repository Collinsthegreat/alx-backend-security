Skip to content
Navigation Menu
thecollekta
alx-backend-security

Type / to search
Code
Issues
Pull requests
Actions
Projects
Security
Insights
Owner avatar
alx-backend-security
Public
thecollekta/alx-backend-security
Go to file
t
Name		
thecollekta
thecollekta
feat(anomaly): implement automated suspicious activity detection
b2874c0
 · 
5 days ago
alx_backend_security
feat(anomaly): implement automated suspicious activity detection
5 days ago
ip_tracking
feat(anomaly): implement automated suspicious activity detection
5 days ago
.gitignore
feat(anomaly): implement automated suspicious activity detection
5 days ago
README.md
feat(anomaly): implement automated suspicious activity detection
5 days ago
manage.py
feat: Implement IP Logging Middleware
last week
requirements.txt
feat(anomaly): implement automated suspicious activity detection
5 days ago
Repository files navigation
README
IP Tracking and Security System
A comprehensive Django application that provides IP tracking, geolocation, rate limiting, and security features.

Features
IP Geolocation: Automatic country and city detection
Request Logging: Detailed request tracking with metadata
IP Blacklisting: Block malicious or suspicious IPs
Rate Limiting: Protect against abuse
Anomaly Detection: Automatic detection of suspicious activity
Admin Interface: Easy management of logs and blocked IPs
Caching: Optimized performance with request caching
Installation
Clone the repository:

git clone https://github.com/yourusername/alx-backend-security.git
cd alx-backend-security
Install dependencies:

pip install -r requirements.txt
Configure your settings in settings.py:

INSTALLED_APPS = [
    # ...
    'ip_tracking',
    'django_celery_beat',
    'django_celery_results',
]

# IP Tracking Settings
SUSPICIOUS_REQUEST_THRESHOLD = 100  # requests per hour
SENSITIVE_PATHS = [
    '/admin/',
    '/login/',
    '/api/auth/',
]

# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
Run migrations:

python manage.py migrate
Start Redis (required for Celery):

# On Linux
sudo service redis-server start

# On Windows
# Download and install Redis from: https://github.com/microsoftarchive/redis/releases
Start Celery worker and beat (in separate terminals):

# Terminal 1 - Celery worker
celery -A alx_backend_security worker --loglevel=info -P solo

# Terminal 2 - Celery beat
celery -A alx_backend_security beat --loglevel=info
Anomaly Detection
The system includes automated anomaly detection that runs hourly to identify suspicious activity:

Detection Rules
High Volume Requests:

Flags IPs making more than 100 requests per hour (configurable via SUSPICIOUS_REQUEST_THRESHOLD)
Logs to SuspiciousIP model with reason 'high_volume'
Sensitive Path Access:

Monitors access to sensitive paths (default: /admin/, /login/, /api/auth/)
Logs to SuspiciousIP model with reason 'sensitive_path'
Monitoring Suspicious Activity
View detected suspicious IPs in the admin interface at /admin/ip_tracking/suspiciousip/ or via the Django shell:

from ip_tracking.models import SuspiciousIP

# Get all active suspicious IPs
suspicious_ips = SuspiciousIP.objects.filter(is_active=True)

# Get IPs flagged for high volume
high_volume_ips = SuspiciousIP.objects.filter(reason='high_volume')
Manual Trigger
You can manually trigger the anomaly detection task:

from ip_tracking.tasks import detect_suspicious_activity

# Run synchronously
result = detect_suspicious_activity()

# Or asynchronously
result = detect_suspicious_activity.delay()
Usage
API Endpoints
Test Geolocation
GET /ip-tracking/test-geo/
POST /ip-tracking/test-geo/
Example Request:

curl -X POST http://127.0.0.1:8000/ip-tracking/test-geo/ \
  -H "Content-Type: application/json" \
  -d '{"ip": "197.210.64.1"}'  # Ghana IP
Example Response:

{
    "ip_address": "197.210.64.1",
    "country": "Ghana",
    "city": "Accra",
    "latitude": 5.55,
    "longitude": -0.2167
}
Rate Limited Login
POST /ip-tracking/login/
Rate Limits:

10 requests/minute for authenticated users
5 requests/minute for anonymous users
Management Commands
Block an IP Address
python manage.py block_ip 192.168.1.100 --reason "Suspicious activity"
Run Anomaly Detection Manually
python manage.py shell -c "from ip_tracking.tasks import detect_suspicious_activity; detect_suspicious_activity()"
Admin Interface
Access the admin panel at http://127.0.0.1:8000/admin/ to:

View and manage request logs
Block/unblock IP addresses
Monitor system activity
Testing
Run Tests
python manage.py test ip_tracking
Manual Testing
Test Rate Limiting

# Test anonymous rate limit (5 requests/minute)
for i in {1..6}; do
    curl http://127.0.0.1:8000/ip-tracking/test-geo/
    echo "---"
done
Test IP Blocking

# Block an IP
python manage.py block_ip 192.168.1.100

# Test blocked IP
curl -H "X-Forwarded-For: 192.168.1.100" http://127.0.0.1:8000/ip-tracking/test-geo/
Configuration
Rate Limiting
Configure in settings.py:

RATELIMIT_GROUP_HANDLERS = {
    'login': 'ip_tracking.ratelimit_handlers.login_handler',
    'geo_test': 'ip_tracking.ratelimit_handlers.geo_test_handler',
}
Caching
Default uses local memory cache. For production, use Redis or Memcached:

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
Security Considerations
IP addresses are hashed before storage
Rate limiting helps prevent brute force attacks
Admin interface is protected by Django's authentication
Sensitive endpoints require authentication
Automated anomaly detection runs hourly to identify suspicious patterns
License
This project is for educational purposes under the ALX ProDEV SE Program.

About
IP Tracking: Security and Analytics

Resources
 Readme
 Activity
Stars
 0 stars
Watchers
 0 watching
Forks
 0 forks
Report repository
Releases
No releases published
Packages
No packages published
Languages
Python
100.0%
Footer
© 2025 GitHub, Inc.
Footer navigation
Terms
Privacy
Security
Status
GitHub Community
Docs
Contact
Manage cookies
Do not share my personal information
alx-backend-security/.gitignore at main · thecollekta/alx-backend-security
