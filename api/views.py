from http.client import BAD_REQUEST

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.gis.geos import Point
from django.core import signing
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.db.transaction import atomic
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _, activate, deactivate_all

import django_filters
from rest_framework import mixins, parsers, renderers, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import list_route, detail_route
from rest_framework.exceptions import ValidationError as DRFValidationError, PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from api.renderers import CSVRenderer
from api.serializers import UserSerializer, GroupSerializer, ServiceSerializer, ProviderSerializer, \
    ProviderTypeSerializer, ServiceAreaSerializer, APILoginSerializer, APIActivationSerializer, \
    PasswordResetRequestSerializer, PasswordResetCheckSerializer, PasswordResetSerializer, \
    ResendActivationLinkSerializer, CreateProviderSerializer, ServiceTypeSerializer, \
    SelectionCriterionSerializer, LanguageSerializer, ServiceSearchSerializer, \
    ProviderFetchSerializer, FeedbackSerializer, NationalitySerializer, ImportSerializer, \
    ServiceTypeWaitTimeSerializer, ServiceTypeQOSSerializer, ServiceTypeFailureSerializer, \
    ServiceTypeContactSerializer, ServiceTypeCommunicationSerializer, \
    ServiceTypeNumServicesSerializer, RequestForServiceSerializer
from email_user.models import EmailUser
from services.models import Service, Provider, ProviderType, ServiceArea, ServiceType, \
    SelectionCriterion, Feedback, Nationality, RequestForService


class TranslatedViewMixin(object):
    def perform_authentication(self, request):
        super().perform_authentication(request)
        # Change current langugage if authentication is successful
        # and we know the user's preference
        if getattr(request.user, 'language', False):
            activate(request.user.language)
        else:
            deactivate_all()


class ServiceInfoGenericViewSet(TranslatedViewMixin, viewsets.GenericViewSet):
    """A view set that allows for translated fields, but doesn't provide any
    specific view methods (like list or detail) by default."""
    pass


class ServiceInfoAPIView(TranslatedViewMixin, APIView):
    pass


class ServiceInfoModelViewSet(TranslatedViewMixin, viewsets.ModelViewSet):
    pass


class FeedbackViewSet(mixins.CreateModelMixin, GenericViewSet):
    """A write-only viewset for feedback"""
    permission_classes = [AllowAny]
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer


class LanguageView(ServiceInfoAPIView):
    """
    Lookup the authenticated user's preferred language.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        return Response({'language': request.user.language})

    def post(self, request):
        serializer = LanguageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.language = serializer.data['language']
        request.user.save()
        return Response()


class UserViewSet(ServiceInfoModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = [IsAuthenticated]
    queryset = EmailUser.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        # Limit to user's own user object
        return self.queryset.filter(pk=self.request.user.pk)

    def update(self, request, *args, **kwargs):
        # Don't allow users to change their email
        instance = self.get_object()
        request.data['email'] = instance.email
        return super().update(request, *args, **kwargs)


class GroupViewSet(ServiceInfoModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class NationalityViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin,
                         ServiceInfoGenericViewSet):
    """
    Read-only API for nationality. You can list them or get one, but
    cannot add, change, or delete them.
    """
    permission_classes = [AllowAny]
    queryset = Nationality.objects.all()
    serializer_class = NationalitySerializer


class ServiceAreaViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin,
                         ServiceInfoGenericViewSet):
    permission_classes = [AllowAny]
    queryset = ServiceArea.objects.all()
    serializer_class = ServiceAreaSerializer


class CharAnyLanguageFilter(django_filters.CharFilter):
    """
    Given the base name of a field that has multiple language versions,
    filter allowing for any of the language versions to contain the
    given value, case-insensitively.

    E.g. if field_name is 'name' and the value given in the query is 'foo',
    then any record where 'name_en', 'name_ar', or 'name_fr' contains 'foo'
    will match.
    """
    def __init__(self, field_name):
        self.field_name = field_name
        super().__init__()

    def filter(self, qset, value):
        if not len(value):
            return qset
        query = Q()
        for lang in ['en', 'ar', 'fr']:
            query |= Q(**{'%s_%s__icontains' % (self.field_name, lang): value})
        return qset.filter(query)


class ServiceTypeNumbersFilter(django_filters.CharFilter):
    """
    Filter service records where their service type has any of the
    numbers given in a comma-separated string.
    """
    def filter(self, qset, value):
        if not len(value):
            return qset
        return qset.filter(type__number__in=[int(s) for s in value.split(',')])


class SortByDistanceFilter(django_filters.CharFilter):
    """Order the results by their distance from a specified lat,long"""
    def filter(self, qset, value):
        if not len(value):
            return qset
        try:
            lat, long = [float(x) for x in value.split(',', 1)]
        except ValueError:
            return qset
        search_point = Point(long, lat)
        return qset.distance(search_point).order_by('distance')

        # We take the coords as lat, long because that's most common
        # (NS position, then EW).  But Point takes (x, y) which means
        # (long, lat) because x is distance east or west, or longitude,
        # and y is distance north or south, or latitude.


class RequestForServiceViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    queryset = RequestForService.objects.all()
    serializer_class = RequestForServiceSerializer


class ServiceFilter(django_filters.FilterSet):
    additional_info = CharAnyLanguageFilter('additional_info')
    area_of_service_name = CharAnyLanguageFilter('area_of_service__name')
    description = CharAnyLanguageFilter('description')
    name = CharAnyLanguageFilter('name')
    type_name = CharAnyLanguageFilter('type__name')
    type_numbers = ServiceTypeNumbersFilter()
    id = django_filters.NumberFilter()
    closest = SortByDistanceFilter()

    class Meta:
        model = Service
        fields = ['area_of_service_name', 'name', 'description', 'additional_info', 'type_name',
                  'type_numbers', 'id']


class ServiceViewSet(ServiceInfoModelViewSet):
    # This docstring shows up when browsing the API in a web browser:
    """
    Service view

    In addition to the usual URLs, you can append 'cancel/' to
    the service's URL and POST to cancel a service that's in
    draft or current state.  (User must be the provider or superuser).
    """
    filter_class = ServiceFilter
    is_search = False
    # The queryset is only here so DRF knows the base model for this View.
    # We override it below in all cases.
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    # All the text fields that are used for full-text searches (?search=XXXXX)
    search_fields = [
        'additional_info_en', 'additional_info_ar', 'additional_info_fr',
        'cost_of_service',
        'description_en', 'description_ar', 'description_fr',
        'name_en', 'name_ar', 'name_fr',

        'area_of_service__name_en', 'area_of_service__name_ar', 'area_of_service__name_fr',

        'type__comments_en', 'type__comments_ar', 'type__comments_fr',
        'type__name_en', 'type__name_ar', 'type__name_fr',

        'provider__description_en', 'provider__description_ar', 'provider__description_fr',
        'provider__focal_point_name_en', 'provider__focal_point_name_ar',
        'provider__focal_point_name_fr',
        'provider__focal_point_phone_number',
        'provider__address_en', 'provider__address_ar', 'provider__address_fr',
        'provider__name_en', 'provider__name_ar', 'provider__name_fr',
        'provider__type__name_en', 'provider__type__name_ar', 'provider__type__name_fr',
        'provider__phone_number',
        'provider__website',
        'provider__user__email',

        'selection_criteria__text_en', 'selection_criteria__text_ar', 'selection_criteria__text_fr',
    ]

    def get_queryset(self):
        # Only make visible the Services owned by the current provider
        # and not archived
        if self.is_search:
            qs = Service.objects.filter(status=Service.STATUS_CURRENT)
        else:
            qs = self.queryset.filter(provider__user=self.request.user)\
                .exclude(status=Service.STATUS_ARCHIVED)\
                .exclude(status=Service.STATUS_CANCELED)
        if not self.request.GET.get('closest', None):
            language = getattr(self.request.user, 'language', None) or 'en'
            qs = qs.order_by('name_' + language)
        return qs

    @detail_route(methods=['post'])
    def cancel(self, request, *args, **kwargs):
        """Cancel a service. Should be current or draft"""
        obj = self.get_object()
        if obj.status not in [Service.STATUS_DRAFT, Service.STATUS_CURRENT]:
            raise DRFValidationError(
                {'status': _('Service record must be current or pending changes to be canceled')})
        obj.cancel()
        return Response()

    @list_route(methods=['get'], permission_classes=[AllowAny])
    def search(self, request, *args, **kwargs):
        """
        Public API for searching public information about the current services
        """
        self.is_search = True
        self.serializer_class = ServiceSearchSerializer
        return super().list(request, *args, **kwargs)


class SelectionCriterionViewSet(ServiceInfoModelViewSet):
    queryset = SelectionCriterion.objects.all()
    serializer_class = SelectionCriterionSerializer

    def get_queryset(self):
        # Only make visible the SelectionCriteria owned by the current provider
        # (attached to services of the current provider)
        return self.queryset.filter(service__provider__user=self.request.user)

    def get_object(self):
        # Users can only access their own records
        # Overriding get_queryset() should be enough, but just in case...
        obj = super().get_object()
        if not obj.provider.user == self.request.user:
            raise PermissionDenied
        return obj


class ProviderTypeViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin,
                          ServiceInfoGenericViewSet):
    """
    Look up provider types.

    (Read-only - no create, update, or delete provided)
    """
    # Unauth'ed users need to be able to read the provider types so
    # they can register as providers.
    permission_classes = [AllowAny]
    queryset = ProviderType.objects.all()
    serializer_class = ProviderTypeSerializer


class ServiceTypeViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin,
                         ServiceInfoGenericViewSet):
    """
    Look up service types.

    (Read-only - no create, update, or delete provided)
    """
    permission_classes = [AllowAny]
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer

    def _do_service_type_report_view(self, serializer_class):
        queryset = self.get_queryset()
        context = self.get_serializer_context()
        serializer = serializer_class(
            queryset, many=True, context=context)
        return Response(serializer.data)

    @list_route(methods=['get', ], url_path='wait-times',
                renderer_classes=[renderers.JSONRenderer, CSVRenderer, ])
    def wait_times(self, request):
        """Wait time feedback aggregated by service type."""
        return self._do_service_type_report_view(ServiceTypeWaitTimeSerializer)

    @list_route(methods=['get', ], url_path='qos',
                renderer_classes=[renderers.JSONRenderer, CSVRenderer, ])
    def qos(self, request):
        """Quality of service delivered feedback aggregated by service type."""
        return self._do_service_type_report_view(ServiceTypeQOSSerializer)

    @list_route(methods=['get', ], url_path='failure',
                renderer_classes=[renderers.JSONRenderer, CSVRenderer, ])
    def failure(self, request):
        """Explanation of Service Delivery Failure by Service Type."""
        return self._do_service_type_report_view(ServiceTypeFailureSerializer)

    @list_route(methods=['get', ], url_path='contact',
                renderer_classes=[renderers.JSONRenderer, CSVRenderer, ])
    def contact(self, request):
        """Difficulties Contacting Service Providers by Service Type."""
        return self._do_service_type_report_view(ServiceTypeContactSerializer)

    @list_route(methods=['get', ], url_path='communication',
                renderer_classes=[renderers.JSONRenderer, CSVRenderer, ])
    def communication(self, request):
        """Satisfaction with Staff Communication by Service Type."""
        return self._do_service_type_report_view(ServiceTypeCommunicationSerializer)

    @list_route(methods=['get', ], url_path='num-services',
                renderer_classes=[renderers.JSONRenderer, CSVRenderer, ])
    def num_services(self, request):
        """Number of Registered Service Providers by Type by Location."""
        # Only top-level service areas
        queryset = self.get_queryset()
        context = self.get_serializer_context()
        serializer = ServiceTypeNumServicesSerializer(
            queryset, many=True, context=context)
        return Response(serializer.data)


class ProviderViewSet(ServiceInfoModelViewSet):
    # This docstring shows up when browsing the API in a web browser:
    """
    Provider view

    For providers to create/update their own data.

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

    @detail_route(methods=['get'], permission_classes=[AllowAny])
    def fetch(self, request, pk=None):
        # Get a provider anonymously using /api/providers/<id>/fetch/
        instance = Provider.objects.get(pk=int(pk))
        serializer = ProviderFetchSerializer(instance, context={'request': request})
        return Response(serializer.data)

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

    def update(self, request, *args, **kwargs):
        """On change to provider via the API, notify via JIRA"""
        response = super().update(request, *args, **kwargs)
        self.get_object().notify_jira_of_change()
        return response

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

            # Create User
            user = get_user_model().objects.create_user(
                email=request.data['email'],
                password=request.data['password'],
                is_active=False
            )
            provider_group, _ = Group.objects.get_or_create(name='Providers')
            user.groups.add(provider_group)

            # Create Provider
            data = dict(request.data, user=user.get_api_url())
            serializer = ProviderSerializer(data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()  # returns provider if we need it
            headers = self.get_success_headers(serializer.data)

            # If we got here without blowing up, send the user's activation email
            user.send_activation_email(request.site, request, data['base_activation_link'])
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


#
# UNAUTHENTICATED views
#

class APILogin(ServiceInfoAPIView):
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
        return Response({'token': token.key,
                         'language': user.language,
                         'is_staff': user.is_staff})


class APIActivationView(ServiceInfoAPIView):
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


class PasswordResetRequest(ServiceInfoAPIView):
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


class PasswordResetCheck(ServiceInfoAPIView):
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


class PasswordReset(ServiceInfoAPIView):
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


class ResendActivationLinkView(ServiceInfoAPIView):
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


class GetExportURLView(APIView):
    """Return a signed time-limited URL for downloading an export"""
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        thing_to_sign = {'u': user.id, 'what': 'export'}
        signature = signing.dumps(thing_to_sign)
        export_url = reverse('export', kwargs={'signature': signature})
        return Response({'url': export_url})


class ImportView(APIView):
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = ImportSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if 'errors' in data:
            return Response(data={'errors': data['errors']}, status=BAD_REQUEST)
        return Response()
