from django.contrib.auth.models import Group
from rest_framework import serializers
from email_user.models import EmailUser
from services.models import Service, Provider, ProviderType


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EmailUser
        fields = ('url', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class ProviderTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProviderType
        fields = ('name_en', 'name_fr', 'name_ar')


class ProviderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Provider
        fields = ('url', 'id', 'name', 'type', 'phone_number', 'website', 'description', 'user')
        extra_kwargs = {
            # Override how serializer comes up with the view name (URL name) for users,
            # because by default it'll base it on the model name from the user field,
            # which is 'email_user', and we're using 'user' as the base for our URL
            # name for users.
            'user': {'view_name': 'user-detail'}
        }


class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Service
        fields = ('url', 'id', 'provider', 'name', 'area_of_service', 'description',
                  'hours_of_service', 'additional_info', 'cost_of_service', 'selection_criteria',
                  'status', 'update_of')
