from rest_framework import serializers


class ClientFilteredPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """
    Custom PrimaryKeyRelatedField that filters the queryset based on the user's client.
    """

    def get_queryset(self):
        request = self.context.get("request", None)
        queryset = super().get_queryset()
        # Ensure the request and user are available in the context
        if request and hasattr(request.user, "client"):
            
            # Filter the queryset based on the user's client
            return queryset.filter(client=request.user.client)

        return queryset.none()  # Return an empty queryset if no request or client
