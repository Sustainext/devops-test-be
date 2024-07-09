from sustainapp.models import UserProfile
from rest_framework import viewsets
from sustainapp.Serializers.UserProfileSerializer import UserProfileSerializer
from rest_framework.response import Response
from rest_framework import status


class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = UserProfile.objects.filter(user=user.id)
        return queryset

    def get_object(self):
        # Override get_object to fetch UserProfile using user_id
        user_id = self.kwargs.get(self.lookup_field)
        return UserProfile.objects.get(user__id=user_id)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        # Update User model if first_name or last_name is in request data
        user = instance.user
        first_name = request.data.get("first_name", None)
        last_name = request.data.get("last_name", None)

        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name

        user.save()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)
