from django.utils import timezone
from authentication.models import UserSafeLock


def handle_failed_login(user):
    safelock, created = UserSafeLock.objects.get_or_create(user=user)
    if created:
        safelock.save()
    safelock.failed_login_attempts += 1
    if safelock.failed_login_attempts >= 3:
        safelock.is_locked = True
        safelock.locked_at = timezone.now()
    safelock.save()


def reset_failed_login_attempts(user):
    safelock, created = UserSafeLock.objects.get_or_create(user=user)
    if created:
        safelock.save()
    safelock.failed_login_attempts = 0
    safelock.is_locked = False
    safelock.locked_at = None
    safelock.save()
