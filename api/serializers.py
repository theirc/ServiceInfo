from django.contrib.auth.models import Group
from rest_framework import serializers
from email_user.models import EmailUser
from services.models import Service, Provider, ProviderType, ServiceArea


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EmailUser
        fields = ('url', 'id', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'id', 'name')


class ProviderTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProviderType
        fields = (
            'url', 'id',
            'name_en', 'name_fr', 'name_ar',
        )


class ProviderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Provider
        fields = ('url', 'id', 'name', 'type', 'phone_number', 'website', 'description', 'user',
                  'number_of_monthly_beneficiaries')
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
        fields = (
            'url', 'id', 'provider', 'name', 'area_of_service', 'description',
            'additional_info', 'cost_of_service', 'selection_criteria',
            'status', 'update_of',
            'location',
            'sunday_open', 'sunday_close',
            'monday_open', 'monday_close',
            'tuesday_open', 'tuesday_close',
            'wednesday_open', 'wednesday_close',
            'thursday_open', 'thursday_close',
            'friday_open', 'friday_close',
            'saturday_open', 'saturday_close',
        )


class ServiceAreaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ServiceArea
        fields = (
            'url',
            'id',
            'name',
            'parent',
            'children',
        )
