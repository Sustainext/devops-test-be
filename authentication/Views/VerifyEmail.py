from django.core.signing import TimestampSigner
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.conf import settings

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
    if email:
        user = User.objects.filter(email=email).first()
        if user.emailaddress_set.filter(email=email).exists():
            return redirect(settings.EMAIL_REDIRECT)
        if user:
            user.emailaddress_set.create(
                email=user.email,
                primary=True,
                verified=True,
            )
            user.save()
    else:
        return redirect(f"{settings.EMAIL_REDIRECT}/token-expired")
    return redirect(settings.EMAIL_REDIRECT)
