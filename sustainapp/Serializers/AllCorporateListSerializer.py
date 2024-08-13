from sustainapp.models import Corporateentity
from rest_framework import serializers

class AllCorporateListSerializer(serializers.ModelSerializer):
    #ToDO: Remove One ID, sending 2 different name of ID just for testing
    checked = serializers.SerializerMethodField()
    corporate_id = serializers.CharField(source="id", read_only=True)
    class Meta:
        model = Corporateentity
        fields = ('id',"corporate_id", 'name',"checked")
    
    def get_checked(self, obj):
        # Define the logic for determining the value of 'checked'
        return False  