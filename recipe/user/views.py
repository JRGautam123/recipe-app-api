"""Views for User API"""

from rest_framework import generics, authentication, permissions
from user.serializers import UserSerializer, AuthTokenSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

# class CreateUserView(generics.CreateAPIView):
#     serializer_class = UserSerializer


class CreateUserView(APIView):
    """View for user api."""
    def post(self, request, *args, **kwargs):
        """When user makes post request to the create user api."""
        serialzer_class = UserSerializer

        serializer = serialzer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateTokenView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
