from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.transaction import atomic
from django.utils.timezone import now

from rest_framework import parsers, renderers, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import list_route, detail_route
from rest_framework.exceptions import ValidationError as DRFValidationError, PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import UserSerializer, GroupSerializer, ServiceSerializer, ProviderSerializer, \
    ProviderTypeSerializer, ServiceAreaSerializer, APILoginSerializer, APIActivationSerializer, \
    PasswordResetRequestSerializer, PasswordResetCheckSerializer, PasswordResetSerializer, \
    ResendActivationLinkSerializer, CreateProviderSerializer, ServiceTypeSerializer, \
    SelectionCriterionSerializer
from email_user.models import EmailUser
from services.models import Service, Provider, ProviderType, ServiceArea, ServiceType, \
    SelectionCriterion
from services.utils import permission_names_to_objects, USER_PERMISSION_NAMES


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


class ServiceAreaViewSet(viewsets.ModelViewSet):
    queryset = ServiceArea.objects.all()
    serializer_class = ServiceAreaSerializer


class ServiceViewSet(viewsets.ModelViewSet):
    # This docstring shows up when browsing the API in a web browser:
    """
    Service view

    In addition to the usual URLs, you can append 'cancel/' to
    the service's URL and POST to cancel a service that's in
    draft or current state.  (User must be the provider or superuser).
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def get_queryset(self):
        # Only make visible the Services owned by the current provider
        return self.queryset.filter(provider__user=self.request.user)

    def get_object(self):
        # Users can only access their own records
        # Overriding get_queryset() should be enough, but just in case...
        obj = super().get_object()
        if not obj.provider.user == self.request.user:
            raise PermissionDenied
        return obj

    @detail_route(methods=['post'])
    def cancel(self, request, *args, **kwargs):
        """Cancel a service. Should be current or draft"""
        obj = self.get_object()
        if obj.status not in [Service.STATUS_DRAFT, Service.STATUS_CURRENT]:
            raise DRFValidationError(
                {'status': 'Service record must be current or pending changes to be canceled'})
        obj.cancel()
        return Response()


class SelectionCriterionViewSet(viewsets.ModelViewSet):
    queryset = SelectionCriterion.objects.all()
    serializer_class = SelectionCriterionSerializer

    def get_queryset(self):
        # Only make visible the SelectionCriteria owned by the current provider
        # (attached to services of the current provider)
        return self.queryset.filter(services__provider__user=self.request.user)

    def get_object(self):
        # Users can only access their own records
        # Overriding get_queryset() should be enough, but just in case...
        obj = super().get_object()
        if not obj.provider.user == self.request.user:
            raise PermissionDenied
        return obj


class ProviderTypeViewSet(viewsets.ModelViewSet):
    queryset = ProviderType.objects.all()
    serializer_class = ProviderTypeSerializer


class ServiceTypeViewSet(viewsets.ModelViewSet):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer


class ProviderViewSet(viewsets.ModelViewSet):
    # This docstring shows up when browsing the API in a web browser:
    """
    Provider view

    In addition to the usual URLs, you can append 'create_provider/' to
    the provider URL and POST to create a new user and provider.

    POST the fields of the provider, except instead of passing the
    user, pass an 'email' and 'password' field so we can create the user
    too.

    The user will be created inactive. An email message will be sent
    to them with a link they'll have to click in order to activate their
    account. After clicking the link, they'll be redirected to the front
    end, logged in and ready to go.
    """

    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer

    def get_queryset(self):
        # If user is authenticated, it's not a create_provider call.
        # Limit visible providers to the user's own.
        if self.request.user.is_authenticated():
            return self.queryset.filter(user=self.request.user)
        return self.queryset.all()  # Add ".all()" to force re-evaluation each time

    def get_object(self):
        # Users can only access their own records
        # Overriding get_queryset() should be enough, but just in case...
        obj = super().get_object()
        if not obj.user == self.request.user:
            raise PermissionDenied
        return obj

    @list_route(methods=['post'], permission_classes=[AllowAny])
    def create_provider(self, request, *args, **kwargs):
        """
        Customized "create provider" API call.

        This is distinct from the built-in 'POST to the list URL'
        call because we need it to work for users who are not
        authenticated (otherwise, they can't register).

        Expected data is basically the same as for creating a provider,
        except that in place of the 'user' field, there should be an
        'email' and 'password' field.  They'll be used to create a new user,
        send them an activation email, and create a provider using
        that user.
        """
        with atomic():  # If we throw an exception anywhere in here, rollback all changes
            serializer = CreateProviderSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = get_user_model().objects.create_user(
                email=request.data['email'],
                password=request.data['password'],
                is_active=False
            )
            # Give them the typical permissions
            # FIXME: we should just do a group
            user.user_permissions.add(*permission_names_to_objects(USER_PERMISSION_NAMES))

            # Now we have a user, let's just call the built-in create
            # method to create the provider for us. We just need to
            # add the 'user' field to the request data.
            if hasattr(request.data, 'dicts'):
                # This is gross but seems to be necessary for now,
                # becausing just setting an item on the MergeDict
                # appears to be a no-op.
                request.data.dicts[0]._mutable = True
                request.data.dicts[0]['user'] = user.get_api_url()
            else:   # pragma: no cover
                # Maybe we have Django 1.9 and MergeDict is gone :-)
                request.data['user'] = user.get_api_url()
                # Make sure this works though
                assert 'user' in request.data
            response = super().create(request, *args, **kwargs)
            # If we got here without blowing up, send the user's activation email
            user.send_activation_email(request.site, request, request.data['base_activation_link'])
        return response


#
# UNAUTHENTICATED views
#

class APILogin(APIView):
    """
    Allow front-end to pass us an email and a password and get
    back an auth token for the user.

    (Adapted from the corresponding view in DRF for our email-based
    user model.)
    """
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)

    def post(self, request):
        serializer = APILoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user.last_login = now()
        user.save(update_fields=['last_login'])
        return Response({'token': token.key})


class APIActivationView(APIView):
    """
    Given a user activation key, activate the user and
    return an auth token.
    """
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)

    def post(self, request):
        serializer = APIActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        activation_key = serializer.validated_data['activation_key']

        try:
            user = get_user_model().objects.activate_user(activation_key=activation_key)
        except DjangoValidationError as e:   # pragma: no cover
            # The serializer already checked the key, so about the only way this could
            # have failed would be due to another request having activated the user
            # between our checking and our trying to activate them ourselves.  Still,
            # it's theoretically possible, so handle it...
            raise DRFValidationError(e.messages)

        token, unused = Token.objects.get_or_create(user=user)
        user.last_login = now()
        user.save(update_fields=['last_login'])
        return Response({'token': token.key, 'email': user.email})


class PasswordResetRequest(APIView):
    """
    View to tell the API that a user wants to reset their password.
    If the provided email is for a valid user, it sends them an
    email with a link they can use.
    """

    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        base_url = serializer.validated_data['base_reset_link']
        user = serializer.validated_data['user']
        user.send_password_reset_email(base_url, request.site)
        return Response()


class PasswordResetCheck(APIView):
    """
    View to check if a password reset key appears to
    be valid (at the moment).
    """
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)

    def post(self, request):
        # The serializer validation does all the work in this one
        serializer = PasswordResetCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'email': serializer.validated_data['user'].email})


class PasswordReset(APIView):
    """
    View to reset a user's password, given a reset key
    and a new password.
    """
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        password = serializer.validated_data['password']
        user.set_password(password)
        user.save()
        token, unused = Token.objects.get_or_create(user=user)
        user.last_login = now()
        user.save(update_fields=['last_login'])
        return Response({'token': token.key, 'email': user.email})


class ResendActivationLinkView(APIView):
    """
    View to resend the activation link for the user
    """
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)

    def post(self, request):
        serializer = ResendActivationLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        user.send_activation_email(request.site, request, request.data['base_activation_link'])
        return Response()
