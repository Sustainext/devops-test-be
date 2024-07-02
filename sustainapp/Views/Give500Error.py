from rest_framework.views import APIView

class Give500Error(APIView):
    def get(self, request):
        raise Exception("This is a test exception")