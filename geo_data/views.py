from rest_framework.permissions import IsAuthenticated
from geo_data.models import Country, State, City
from geo_data.serializers import CountrySerializer, StateSerializer, CitySerializer,CityCreateSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

class CityCreateView(APIView):
    def post(self, request):
        city_name = request.data.get("city_name")
        state_id = request.data.get("state")

        if not city_name or not state_id:
            return Response({"detail": "Both 'city_name' and 'state' are required."}, status=status.HTTP_400_BAD_REQUEST)

        if City.objects.filter(city_name=city_name, state_id=state_id).exists():
            return Response(
                {"detail": f"City '{city_name}' linked to state ID {state_id} already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CityCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CountryListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        countries = Country.objects.all()
        serializer = CountrySerializer(countries, many=True)
        return Response(serializer.data)
        


class StateListByCountryView(APIView):
    def get(self, request):
        country_id = request.query_params.get('country_id')
        if not country_id:
            return Response({"error": "country_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        states = State.objects.filter(country_id=country_id)
        serializer = StateSerializer(states, many=True)
        return Response(serializer.data)


class CityListByStateView(APIView):
    def get(self, request):
        state_id = request.query_params.get('state_id')
        if not state_id:
            return Response({"error": "state_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        cities = City.objects.filter(state_id=state_id)
        serializer = CitySerializer(cities, many=True)
        return Response(serializer.data)
