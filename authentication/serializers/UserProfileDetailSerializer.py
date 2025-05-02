from rest_framework import serializers
from authentication.models import UserProfile


class UserProfileDetailSerializer(serializers.ModelSerializer):
    """Serializer for getting and updating user profile details"""
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    designation = serializers.CharField(source='user.job_title')
    department = serializers.CharField(source='user.department')
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    profile_pic = serializers.ImageField(source='profile_picture', required=False, allow_null=True)
    custom_role = serializers.CharField(source='user.custom_role.name', read_only=True)
    user_id = serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = UserProfile
        fields = (
            'id',
            'user_id',
            'first_name',
            'last_name',
            'designation',
            'department',
            'phone',
            'profile_pic',
            'custom_role',
        )

    def update(self, instance, validated_data):
        # Handle user fields update
        user_data = validated_data.pop('user', {})
        user = instance.user

        if 'first_name' in user_data:
            user.first_name = user_data['first_name']
        if 'last_name' in user_data:
            user.last_name = user_data['last_name']
        if 'job_title' in user_data:
            user.job_title = user_data['job_title']
        if 'department' in user_data:
            user.department = user_data['department']

        user.save()

        # Update UserProfile fields
        if 'phone' in validated_data:
            instance.phone = validated_data['phone']
        if 'profile_picture' in validated_data:
            instance.profile_picture = validated_data['profile_picture']

        instance.save()

        return instance
