from django.db import models

 
class Country(models.Model):
    sortname = models.CharField(max_length=3)
    country_name = models.CharField(max_length=250)
    slug = models.CharField(max_length=100, null=True, blank=True)
    status = models.IntegerField(default=1)

    class Meta:
        db_table = "geo_data_country"
    
    def __str__(self):
        return self.country_name


class State(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='states')
    state_name = models.CharField(max_length=250)

    class Meta:
        db_table = "geo_data_state"

    def __str__(self):
        return self.state_name


class City(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, db_column="state_id")
    city_name = models.CharField(max_length=250)

    class Meta:
        db_table = "geo_data_city"
    
    def __str__(self):
        return self.city_name
