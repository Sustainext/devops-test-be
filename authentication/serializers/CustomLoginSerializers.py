import logging
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# Loggers
logger = logging.getLogger()
warning_handler = logging.FileHandler("warning.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
warning_handler.setFormatter(formatter)
warning_handler.setLevel(logging.INFO)
logger.addHandler(warning_handler)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["client_id"] = user.client_id

        return token
