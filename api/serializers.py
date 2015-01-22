from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _

from rest_framework import exceptions, serializers

from email_user.models import EmailUser, SHA1_RE
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
    Both validates the call parameters and authenticates
    the user, returning the user in the validated_data
    if successful.

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


class APIActivationSerializer(serializers.Serializer):
    """
    Serializer for our "activate" API.

    Raises ValidationError if the call is invalid.
    """
    activation_key = serializers.CharField()

    def validate(self, attrs):
        activation_key = attrs.get('activation_key')
        if activation_key:
            if not SHA1_RE.search(activation_key):
                msg = _('Activation key is not a valid format. Make sure the activation link '
                        'has been copied correctly.')
                raise exceptions.ValidationError({'activation_key': msg})
            User = get_user_model()
            try:
                user = User.objects.get(activation_key=activation_key)
            except User.DoesNotExist:
                msg = _('Activation key is invalid or has already been used.')
                raise exceptions.ValidationError({'activation_key': msg})
            else:
                if user.activation_key_expired():
                    user.delete()
                    msg = _('Activation link has expired.')
                    raise exceptions.ValidationError({'activation_key': msg})
        else:
            msg = _('Must include "activation_key"')
            raise exceptions.ValidationError({'activation_key': msg})
        return attrs
