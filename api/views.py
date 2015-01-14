from django.contrib.auth.models import Group
from rest_framework import viewsets
from email_user.models import EmailUser
from .serializers import UserSerializer, GroupSerializer, ServiceSerializer, ProviderSerializer, \
    ProviderTypeSerializer
from services.models import Service, Provider, ProviderType


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = EmailUser.objects.all()
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


class ProviderTypeViewSet(viewsets.ModelViewSet):
    queryset = ProviderType.objects.all()
    serializer_class = ProviderTypeSerializer


class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
