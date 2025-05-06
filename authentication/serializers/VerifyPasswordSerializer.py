from rest_framework.serializers import Serializer, CharField

class VerifyPasswordSerializer(Serializer):
    password = CharField(required=True, write_only=True)
