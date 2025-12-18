from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated

from .serializers import TempRegisterSerializer, CustomTokenObtainPairSerializer, RoleSerializer
from .models import Role

class TempRegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = TempRegisterSerializer(data=request.data)
        if serializer.is_valid():
            role, _ = Role.objects.get_or_create(id=1, defaults={"name":"customer", "display_name":"customer", "description":'test', "permissions":'{}'})
            user = serializer.save(role=role)
            return Response({"detail":"user registered"})
        return Response({"errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class= CustomTokenObtainPairSerializer


class RoleViewset(viewsets.ModelViewSet):
    serializer_class = RoleSerializer
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = Role.objects.all()

