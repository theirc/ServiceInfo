from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _

from rest_framework import exceptions, serializers

from email_user.forms import EmailUserCreationForm
from email_user.models import EmailUser
from services.models import Service, Provider, ProviderType, ServiceType, ServiceArea, \
    SelectionCriterion


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


class CreateProviderSerializer(ProviderSerializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    base_activation_link = serializers.URLField()

    class Meta:
        model = Provider
        fields = [field for field in ProviderSerializer.Meta.fields
                  if field not in ['user']]
        fields += ['email', 'password', 'base_activation_link']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        form = EmailUserCreationForm(data={
            'email': email,
            'password1': password,
            'password2': password,
            })
        if not form.is_valid():
            raise exceptions.ValidationError(form.errors)
        return attrs


class ServiceTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ServiceType
        fields = (
            'url',
            'number',
            'name_en', 'name_fr', 'name_ar',
            'comments_en', 'comments_fr', 'comments_ar',
        )


class SelectionCriterionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SelectionCriterion
        fields = ('url', 'id', 'text_en', 'text_ar', 'text_fr')


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
            'type',
        )

    def save(self, **kwargs):
        # Force the value of the provider to be that of the user who's
        # creating or modifying the record
        user = self.context['request'].user
        kwargs['provider'] = Provider.objects.get(user=user)
        super().save(**kwargs)


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
        user = authenticate(email=email, password=password)

        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Unable to log in with provided credentials.')
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
        User = get_user_model()
        try:
            User.objects.get(activation_key=activation_key)
        except User.DoesNotExist:
            msg = _('Activation key is invalid. Check that it was copied correctly '
                    'and has not already been used.')
            raise exceptions.ValidationError({'activation_key': msg})
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for our API to request a password reset.

    Validates the email.
    """
    email = serializers.EmailField()
    base_reset_link = serializers.URLField()

    def validate(self, attrs):
        User = get_user_model()
        try:
            attrs['user'] = User.objects.get(email__iexact=attrs.get('email'))
        except User.DoesNotExist:
            msg = _("No user with that email")
            raise exceptions.ValidationError({'email': msg})
        return attrs


class PasswordResetCheckSerializer(serializers.Serializer):
    """
    Serializer for our API to check if a password
    reset key appears to be valid.
    """
    email = serializers.EmailField()
    key = serializers.CharField()

    def validate(self, attrs):
        key = attrs.get('key')
        user = get_user_model().objects.validate_password_reset_key(key)
        if not user:
            msg = _("Password reset key is not valid")
            raise exceptions.ValidationError(msg)
        attrs['user'] = user
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for our API to reset a password.
    """
    password = serializers.CharField()
    key = serializers.CharField()

    def validate(self, attrs):
        key = attrs.get('key')
        user = get_user_model().objects.validate_password_reset_key(key)
        if not user:
            msg = _("Password reset key is not valid")
            raise exceptions.ValidationError(msg)
        attrs['user'] = user
        return attrs


class ResendActivationLinkSerializer(serializers.Serializer):
    email = serializers.EmailField()
    base_activation_link = serializers.URLField()

    def validate(self, attrs):
        email = attrs.get('email')
        try:
            user = get_user_model().objects.get(email__iexact=email)
        except get_user_model().DoesNotExist:
            msg = _("No user with that email")
            raise exceptions.ValidationError({'email': msg})
        if not user.has_valid_activation_key():
            msg = _("User is not pending activation")
            raise exceptions.ValidationError({'email': msg})
        attrs['user'] = user
        return attrs
