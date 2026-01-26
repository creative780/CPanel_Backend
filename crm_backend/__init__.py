# Make Celery optional - fail gracefully if import fails (e.g., kombu entry points issue on Python 3.13)
try:
    from .celery import app as celery_app  # type: ignore
    __all__ = ("celery_app",)
except (ImportError, ModuleNotFoundError, Exception):  # pragma: no cover
    # Silently fail if Celery can't be imported
    # This allows Django to start even if Celery has issues
    celery_app = None  # type: ignore
    __all__ = ()
