from rest_framework import serializers
from authentication.models import UserProfile


class UserProfileDetailSerializer(serializers.ModelSerializer):
    """Serializer for getting and updating user profile details"""
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    designation = serializers.CharField(source='user.job_title')
    department = serializers.CharField(source='user.department')
    job_description = serializers.CharField(source='user.job_description')
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
            "job_description",
            'phone',
            'profile_pic',
            'custom_role',
        )

    def update(self, instance, validated_data):
        # Handle user fields update
        user_data = validated_data.pop('user', {})
        user = instance.user

        # Update user fields with dictionary unpacking
        user_fields = {
            'first_name': user_data.get('first_name', user.first_name),
            'last_name': user_data.get('last_name', user.last_name),
            'job_title': user_data.get('job_title', user.job_title),
            'department': user_data.get('department', user.department),
            'job_description': user_data.get('job_description', user.job_description),
        }

        for field, value in user_fields.items():
            setattr(user, field, value)

        user.save()

        # Update UserProfile fields
        profile_fields = {
            'phone': validated_data.get('phone', instance.phone),
            'profile_picture': validated_data.get('profile_picture', instance.profile_picture)
        }

        for field, value in profile_fields.items():
            setattr(instance, field, value)

        instance.save()

        return instance
