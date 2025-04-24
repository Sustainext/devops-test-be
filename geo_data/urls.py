from django.urls import path
from .views import CityCreateView, CountryListView, StateListByCountryView, CityListByStateView


urlpatterns = [
    path('cities/create/', CityCreateView.as_view(), name='city-create'),
    path('countries/', CountryListView.as_view(), name='country-list'),
    path('states/', StateListByCountryView.as_view(), name='state-list-by-country'),
    path('cities/', CityListByStateView.as_view(), name='city-list-by-state'),
]
