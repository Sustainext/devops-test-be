from django.db import models


class ClientFiltering(models.Manager):
    def by_client_id(self, client_id):
        return self.get_queryset().filter(client_id=client_id)
