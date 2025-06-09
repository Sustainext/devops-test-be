from django.core.signing import TimestampSigner
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.conf import settings
from authentication.models import UserEmailVerification

User = get_user_model()


def generate_verification_token(user):
    signer = TimestampSigner()
    return signer.sign(user.email)


def verify_token(token, max_age=259200):
    signer = TimestampSigner()
    try:
        email = signer.unsign(token, max_age=max_age)
        return email
    except Exception:
        return None


def verify_email(request, token):
    email = verify_token(token)
    if not email:
        return redirect(f"{settings.EMAIL_REDIRECT}/token-expired")

    user = User.objects.get(email=email)
    if not user:
        return redirect(f"{settings.EMAIL_REDIRECT}/invalid-user")

    ver_record = UserEmailVerification.objects.get(user=user)
    if ver_record:
        if ver_record.token != token or ver_record.is_token_expired():
            return redirect(f"{settings.EMAIL_REDIRECT}/token-expired")
        ver_record.mark_verified()

    if user.emailaddress_set.filter(email=email).exists():
        return redirect(settings.EMAIL_REDIRECT)

    user.emailaddress_set.create(
        email=user.email,
        primary=True,
        verified=True,
    )
    return redirect(settings.EMAIL_REDIRECT)
