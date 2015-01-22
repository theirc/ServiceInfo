from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _

from rest_framework import exceptions, serializers

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
        fields = ('url', 'id', 'name_en', 'name_ar', 'name_fr',
                  'type', 'phone_number', 'website',
                  'description_en', 'description_ar', 'description_fr',
                  'user', 'number_of_monthly_beneficiaries')
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
            'url', 'id', 'provider',
            'name_en', 'name_ar', 'name_fr',
            'area_of_service',
            'description_en', 'description_ar', 'description_fr',
            'additional_info_en', 'additional_info_ar', 'additional_info_fr',
            'cost_of_service', 'selection_criteria',
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
            'name_en',
            'name_ar',
            'name_fr',
            'parent',
            'children',
        )


class APILoginSerializer(serializers.Serializer):
    """
    Serializer for our "login" API.

    Adapted from authtoken/serializers.py for our email-based user model
    """
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(email=email, password=password)

            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise exceptions.ValidationError(msg)
            else:
                msg = _('Unable to log in with provided credentials.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Must include "email" and "password"')
            raise exceptions.ValidationError(msg)

        attrs['user'] = user
        return attrs
