from .base import *


# ==============================================================================
# DJANGO SECURITY SETTINGS
# ==============================================================================

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False

SECURE_HSTS_SECONDS = 60 * 60 * 24 * 7 * 26  # 6 monts
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_SSL_REDIRECT = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
