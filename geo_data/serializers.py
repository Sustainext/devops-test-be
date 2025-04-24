from rest_framework import serializers
from .models import Country, State, City


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'sortname', 'country_name', 'slug', 'status']

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'state_name', 'country']

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'city_name', 'state']



class CityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['city_name','state']