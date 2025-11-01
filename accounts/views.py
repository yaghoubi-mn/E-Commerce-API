from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import TempRegisterSerializer, CustomTokenObtainPairSerializer

class TempRegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = TempRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"detail":"user registered", 'data': user})
        return Response({"errors":serializer.error_messages}, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class= CustomTokenObtainPairSerializer


