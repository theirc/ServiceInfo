from django import forms
from django.contrib.auth import get_user_model
from django.contrib.gis.forms import PointField
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from services.models import Provider, Service, SelectionCriterion, ServiceType, ServiceArea, \
    ProviderType


def try_to_get_one(model, **query_kwargs):
    """
    Return the best match instance of `model` using as many of the given
    query args as we can.  Returns None if we can't find a combination of
    the args that gives us exactly one result.
    :param model:
    :param query_kwargs:
    :return:
    """
    # If all the args gives us one result, use it.
    qset = model.objects.filter(**query_kwargs)
    if qset.count() == 1:
        return qset[0]
    if qset.count() > 1:
        # We got more than one result even using all the args, so
        # it's hopeless.  Removing args cannot get us down to 1 result.
        return None

    # Start a breadth-first search for a workable combination.
    # First try all the ways of dropping one of the kwargs.
    # If we're not successful, then start calling this recursively,
    # each time starting by dropping a different arg.

    # Try dropping just one
    keys = query_kwargs.keys()
    if len(keys) <= 1:
        return None
    for key_to_omit in keys:
        kwargs_to_use = dict(query_kwargs)
        del kwargs_to_use[key_to_omit]
        qset = model.objects.filter(**kwargs_to_use)
        if qset.count() == 1:
            return qset[0]
    # No luck - recurse
    for key_to_omit in keys:
        kwargs_to_use = dict(query_kwargs)
        del kwargs_to_use[key_to_omit]
        result = try_to_get_one(model, **kwargs_to_use)
        if result:
            return result


# We're using form widgets to adapt from the values coming from
# the imported spreadsheet object to the values that Django
# would commonly expect in a form submission.

class ProviderTypeWidget(forms.Widget):
    def value_from_datadict(self, data, files, name):
        """
        Find the relevant provider type record and return its ID

        Try to allow exact specification of a type but be forgiving
        if they misspell a field or two or leave some blank and the
        rest is still enough to identify a unique provider type:
        """
        provider_type = try_to_get_one(
            ProviderType,
            number=data['type__number'],
            name_en=data['type__name_en'],
            name_ar=data['type__name_ar'],
            name_fr=data['type__name_fr'])
        if provider_type:
            return provider_type.id


class UserWidget(forms.Widget):
    def value_from_datadict(self, data, files, name):
        User = get_user_model()
        return User.objects.get(email__iexact=data['email']).id


class ProviderForm(forms.ModelForm):
    # Validate provider data as imported in an Excel spreadsheet edited from an export
    type = forms.ModelChoiceField(
        queryset=ProviderType.objects.all(),
        widget=ProviderTypeWidget
    )
    user = forms.ModelChoiceField(
        queryset=get_user_model().objects.all(),
        widget=UserWidget
    )

    class Meta:
        model = Provider
        # Setting fields to '__all__' here is reasonably safe since we
        # are careful elsewhere to only export and import certain fields.
        fields = '__all__'


class ServiceTypeWidget(forms.Widget):
    # Widget that looks up a service type object from
    # the type__name_en, type__name_ar, and type__name_fr fields
    # in the provided data.
    def value_from_datadict(self, data, files, name):
        """
        Given a dictionary of data and this widget's name, returns the value
        of this widget. Returns None if it's not provided.
        """
        service_type = try_to_get_one(
            ServiceType,
            name_en=data['type__name_en'],
            name_ar=data['type__name_ar'],
            name_fr=data['type__name_fr'],
        )
        if service_type:
            return service_type.id
        raise ValidationError(_('There is no service type with English name %r')
                              % data['type__name_en'])


class ServiceAreaWidget(forms.Widget):
    # Like ServiceTypeWidget but for ServiceArea
    def value_from_datadict(self, data, files, name):
        """
        Given a dictionary of data and this widget's name, returns the value
        of this widget. Returns None if it's not provided.
        """
        try:
            return ServiceArea.objects.get(
                name_en=data['area_of_service__name_en'],
                name_ar=data['area_of_service__name_ar'],
                name_fr=data['area_of_service__name_fr'],
            ).id
        except ServiceArea.DoesNotExist:
            raise ValidationError(_('There is no service area with English name %r')
                                  % data['area_of_service__name_en'])


class ProviderWidget(forms.Widget):
    def value_from_datadict(self, data, files, name):
        return int(data['provider__id'])


class PointWidget(forms.Widget):
    def value_from_datadict(self, data, files, name):
        return Point(data['longitude'], data['latitude'])


class ServiceForm(forms.ModelForm):
    type = forms.ModelChoiceField(
        queryset=ServiceType.objects.all(),
        widget=ServiceTypeWidget
    )
    area_of_service = forms.ModelChoiceField(
        queryset=ServiceArea.objects.all(),
        widget=ServiceAreaWidget
    )
    provider = forms.ModelChoiceField(
        queryset=Provider.objects.all(),
        widget=ProviderWidget
    )
    location = PointField(
        widget=PointWidget
    )

    class Meta:
        model = Service
        exclude = ['status']
        # Setting fields to '__all__' here is reasonably safe since we
        # are careful elsewhere to only export and import certain fields.
        fields = '__all__'


class SelectionCriterionForm(forms.ModelForm):
    class Meta:
        model = SelectionCriterion
        # Setting fields to '__all__' here is reasonably safe since we
        # are careful elsewhere to only export and import certain fields.
        fields = '__all__'
