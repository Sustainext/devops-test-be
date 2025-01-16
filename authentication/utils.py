from django.utils import timezone
from authentication.models import UserSafeLock
from datetime import timedelta

LOCK_WINDOW = 15
UNLOCK_DURATION = 2  # This is in Hrs


def handle_failed_login(user):
    safelock, created = UserSafeLock.objects.get_or_create(user=user)
    if created:
        safelock.save()

    if safelock.is_locked:
        return safelock

    if safelock.last_failed_at:
        time_difference = timezone.now() - safelock.last_failed_at
        if time_difference > timedelta(minutes=LOCK_WINDOW):
            safelock.failed_login_attempts = 1
        else:
            safelock.failed_login_attempts += 1
    else:
        safelock.failed_login_attempts = 1

    safelock.last_failed_at = timezone.now()

    if safelock.failed_login_attempts >= 3:
        safelock.is_locked = True
        safelock.locked_at = timezone.now()

    safelock.save()
    return safelock


def reset_failed_login_attempts(user):
    safelock, created = UserSafeLock.objects.get_or_create(user=user)
    if created:
        safelock.save()
    safelock.failed_login_attempts = 0
    safelock.is_locked = False
    safelock.locked_at = None
    safelock.last_failed_at = None
    safelock.save()
