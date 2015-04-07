from django import forms
from django.contrib.auth import get_user_model
from django.contrib.gis.forms import PointField
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from services.models import Provider, Service, SelectionCriterion, ServiceType, ServiceArea, \
    ProviderType


# We're using form widgets to adapt from the values coming from
# the imported spreadsheet object to the values that Django
# would commonly expect in a form submission.

class ProviderTypeWidget(forms.Widget):
    def value_from_datadict(self, data, files, name):
        return ProviderType.objects.get(
            number=data['type__number'],
            name_en=data['type__name_en'],
            name_ar=data['type__name_ar'],
            name_fr=data['type__name_fr'],
        ).id


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
        try:
            return ServiceType.objects.get(
                name_en=data['type__name_en'],
                name_ar=data['type__name_ar'],
                name_fr=data['type__name_fr'],
            ).id
        except ServiceType.DoesNotExist:
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
