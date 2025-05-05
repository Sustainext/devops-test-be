from rest_framework.views import APIView
from rest_framework.response import Response
from authentication.models import UserProfile
from authentication.serializers.UserProfileDetailSerializer import UserProfileDetailSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound

class UserProfileDetailView(APIView):
    """
    User Profile API
    A view for retrieving, updating a user profile.

    This view provides endpoints to:
    - GET: Retrieve the authenticated user's profile
    - PUT: Update the authenticated user's profile (supports partial updates via query param)

    Authorization is required for all endpoints.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return self.queryset.get(user=self.request.user)
        except UserProfile.DoesNotExist:
            raise NotFound("User profile not found")

    def get(self, request):
        user_profile = self.get_object()
        serializer = self.serializer_class(user_profile)
        return Response(serializer.data)

    def put(self, request):
        user_profile = self.get_object()
        partial = request.query_params.get('partial', False)
        serializer = self.serializer_class(user_profile, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
