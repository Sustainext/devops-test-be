from sustainapp.models import Corporateentity
from rest_framework import serializers

class AllCorporateListSerializer(serializers.ModelSerializer):
    #ToDO: Remove One ID, sending 2 different name of ID just for testing
    checked = serializers.SerializerMethodField()
    ownershipRatio = serializers.SerializerMethodField()
    class Meta:
        model = Corporateentity
        fields = ('id',"ownershipRatio", 'name',"checked")
    
    def get_checked(self, obj):
        # Define the logic for determining the value of 'checked'
        return False
    
    def get_ownershipRatio(self, obj):
        # Return an empty string for ownershipRatio
        return ""