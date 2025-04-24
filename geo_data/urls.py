from django.urls import path
from .views import CityCreateView, CountryListView, StateListByCountryView, CityListByStateView


urlpatterns = [
    # path('api/city/', CityCreateView.as_view(), name='city-create'),
    path('api/cities/create/', CityCreateView.as_view(), name='city-create'),
    path('api/countries/', CountryListView.as_view(), name='country-list'),
    path('api/states/', StateListByCountryView.as_view(), name='state-list-by-country'),
    path('api/cities/', CityListByStateView.as_view(), name='city-list-by-state'),
]
