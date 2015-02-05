from django.conf import settings
from django.contrib.gis.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _, get_language

from services.tasks import email_provider_about_service_approval_task


class NameInCurrentLanguageMixin(object):
    @property
    def name(self):
        # Try to return the name field of the currently selected language
        # if we have such a field and it has something in it.
        # Otherwise, punt and return the first of the English, Arabic, or
        # French names that has anything in it.
        language = get_language()
        field_name = 'name_%s' % language[:2]
        if hasattr(self, field_name) and getattr(self, field_name):
            return getattr(self, field_name)
        return self.name_en or self.name_ar or self.name_fr


class ProviderType(NameInCurrentLanguageMixin, models.Model):
    number = models.IntegerField(unique=True)
    name_en = models.CharField(
        _("name in English"),
        max_length=256,
        default='',
        blank=True,
    )
    name_ar = models.CharField(
        _("name in Arabic"),
        max_length=256,
        default='',
        blank=True,
    )
    name_fr = models.CharField(
        _("name in French"),
        max_length=256,
        default='',
        blank=True,
    )

    def __str__(self):
        return self.name

    def get_api_url(self):
        return reverse('providertype-detail', args=[self.id])


class Provider(NameInCurrentLanguageMixin, models.Model):
    name_en = models.CharField(
        # Translators: Provider name
        _("name in English"),
        max_length=256,  # Length is a guess
        default='',
        blank=True,
    )
    name_ar = models.CharField(
        # Translators: Provider name
        _("name in Arabic"),
        max_length=256,  # Length is a guess
        default='',
        blank=True,
    )
    name_fr = models.CharField(
        # Translators: Provider name
        _("name in French"),
        max_length=256,  # Length is a guess
        default='',
        blank=True,
    )
    type = models.ForeignKey(
        ProviderType,
        verbose_name=_("type"),
    )
    phone_number = models.CharField(
        _("phone number"),
        max_length=20,
    )
    website = models.URLField(
        _("website"),
        blank=True,
        default='',
    )
    description_en = models.TextField(
        # Translators: Provider description
        _("description in English"),
        default='',
        blank=True,
    )
    description_ar = models.TextField(
        # Translators: Provider description
        _("description in Arabic"),
        default='',
        blank=True,
    )
    description_fr = models.TextField(
        # Translators: Provider description
        _("description in French"),
        default='',
        blank=True,
    )
    user = models.OneToOneField(
        to=settings.AUTH_USER_MODEL,
        verbose_name=_('user'),
        help_text=_('user account for this provider'),
    )
    number_of_monthly_beneficiaries = models.IntegerField(
        _("number of targeted beneficiaries monthly"),
    )

    def __str__(self):
        return self.name_en

    def get_api_url(self):
        return reverse('provider-detail', args=[self.id])


class ServiceArea(NameInCurrentLanguageMixin, models.Model):
    name_en = models.CharField(
        _("name in English"),
        max_length=256,
        default='',
        blank=True,
    )
    name_ar = models.CharField(
        _("name in Arabic"),
        max_length=256,
        default='',
        blank=True,
    )
    name_fr = models.CharField(
        _("name in French"),
        max_length=256,
        default='',
        blank=True,
    )
    parent = models.ForeignKey(
        to='self',
        verbose_name=_('parent area'),
        help_text=_('the area that contains this area'),
        null=True,
        blank=True,
        related_name='children',
    )
    region = models.PolygonField(
        blank=True,
        null=True,
    )

    objects = models.GeoManager()

    def get_api_url(self):
        return reverse('servicearea-detail', args=[self.id])


class SelectionCriterion(models.Model):
    """
    A selection criterion limits who can receive the service.
    It's just a text string. E.g. "age under 18".
    """
    text_en = models.CharField(max_length=100, blank=True, default='')
    text_fr = models.CharField(max_length=100, blank=True, default='')
    text_ar = models.CharField(max_length=100, blank=True, default='')

    class Meta(object):
        verbose_name_plural = _("selection criteria")


class ServiceType(NameInCurrentLanguageMixin, models.Model):
    number = models.IntegerField(unique=True)
    name_en = models.CharField(
        _("name in English"),
        max_length=256,
        default='',
        blank=True,
    )
    name_ar = models.CharField(
        _("name in Arabic"),
        max_length=256,
        default='',
        blank=True,
    )
    name_fr = models.CharField(
        _("name in French"),
        max_length=256,
        default='',
        blank=True,
    )

    comments_en = models.CharField(
        _("comments in English"),
        max_length=512,
        default='',
        blank=True,
    )
    comments_ar = models.CharField(
        _("comments in Arabic"),
        max_length=512,
        default='',
        blank=True,
    )
    comments_fr = models.CharField(
        _("comments in French"),
        max_length=512,
        default='',
        blank=True,
    )

    def __str__(self):
        # Try to return the name field of the currently selected language
        # if we have such a field and it has something in it.
        # Otherwise, punt and return the English, French, or Arabic name,
        # in that order.
        language = get_language()
        field_name = 'name_%s' % language[:2]
        if hasattr(self, field_name) and getattr(self, field_name):
            return getattr(self, field_name)
        return self.name_en or self.name_fr or self.name_ar

    def get_api_url(self):
        return reverse('servicetype-detail', args=[self.id])


class ServiceManager(models.GeoManager):
    def get_queryset(self):
        return super().get_queryset().exclude(status=Service.STATUS_ARCHIVED)


class Service(NameInCurrentLanguageMixin, models.Model):
    provider = models.ForeignKey(
        Provider,
        verbose_name=_("provider"),
    )
    name_en = models.CharField(
        # Translators: Service name
        _("name in English"),
        max_length=256,
        default='',
        blank=True,
    )
    name_ar = models.CharField(
        # Translators: Service name
        _("name in Arabic"),
        max_length=256,
        default='',
        blank=True,
    )
    name_fr = models.CharField(
        # Translators: Service name
        _("name in French"),
        max_length=256,
        default='',
        blank=True,
    )
    area_of_service = models.ForeignKey(
        ServiceArea,
        verbose_name=_("area of service"),
    )
    description_en = models.TextField(
        # Translators: Service description
        _("description in English"),
        default='',
        blank=True,
    )
    description_ar = models.TextField(
        # Translators: Service description
        _("description in Arabic"),
        default='',
        blank=True,
    )
    description_fr = models.TextField(
        # Translators: Service description
        _("description in French"),
        default='',
        blank=True,
    )
    additional_info_en = models.TextField(
        _("additional information in English"),
        blank=True,
        default='',
    )
    additional_info_ar = models.TextField(
        _("additional information in Arabic"),
        blank=True,
        default='',
    )
    additional_info_fr = models.TextField(
        _("additional information in French"),
        blank=True,
        default='',
    )
    cost_of_service = models.TextField(
        _("cost of service"),
        blank=True,
        default='',
    )
    selection_criteria = models.ManyToManyField(
        SelectionCriterion,
        related_name='services',
        verbose_name=_("selection criteria"),
        blank=True,
    )

    # Note: we don't let multiple versions of a service record pile up - there
    # should be no more than two, one in current status and/or one in some other
    # status.
    STATUS_DRAFT = 'draft'
    STATUS_CURRENT = 'current'
    STATUS_REJECTED = 'rejected'
    STATUS_CANCELED = 'canceled'
    STATUS_ARCHIVED = 'archived'
    STATUS_CHOICES = (
        # New service or edit of existing service is pending approval
        (STATUS_DRAFT, _('draft')),
        # This Service has been approved and not superseded. Only services with
        # status 'current' appear in the public interface.
        (STATUS_CURRENT, _('current')),
        # The staff has rejected the service submission or edit
        (STATUS_REJECTED, _('rejected')),
        # The provider has canceled service. They can do this on draft or current services.
        # It no longer appears in the public interface.
        (STATUS_CANCELED, _('canceled')),
        # The record is obsolete and we don't want to see it anymore
        (STATUS_ARCHIVED, _('archived')),
    )
    status = models.CharField(
        _('status'),
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
    )
    update_of = models.ForeignKey(
        'self',
        help_text=_('If a service record represents a modification of an existing service '
                    'record that is still pending approval, this field links to the '
                    'existing service record.'),
        null=True,
        blank=True,
        related_name='pending_update',
        unique=True,
    )

    location = models.PointField(
        _('location'),
        blank=True,
        null=True,
    )

    # Open & close hours by day. If None, service is closed that day.
    sunday_open = models.TimeField(null=True, blank=True)
    sunday_close = models.TimeField(null=True, blank=True)
    monday_open = models.TimeField(null=True, blank=True)
    monday_close = models.TimeField(null=True, blank=True)
    tuesday_open = models.TimeField(null=True, blank=True)
    tuesday_close = models.TimeField(null=True, blank=True)
    wednesday_open = models.TimeField(null=True, blank=True)
    wednesday_close = models.TimeField(null=True, blank=True)
    thursday_open = models.TimeField(null=True, blank=True)
    thursday_close = models.TimeField(null=True, blank=True)
    friday_open = models.TimeField(null=True, blank=True)
    friday_close = models.TimeField(null=True, blank=True)
    saturday_open = models.TimeField(null=True, blank=True)
    saturday_close = models.TimeField(null=True, blank=True)

    type = models.ForeignKey(
        ServiceType,
        verbose_name=_("type"),
    )

    objects = ServiceManager()

    def __str__(self):
        return self.name_en

    def get_api_url(self):
        return reverse('service-detail', args=[self.id])

    def email_provider_about_approval(self):
        """Schedule a task to send an email to the provider"""
        # FIXME: Somebody needs to call this at the appropriate time :-)
        email_provider_about_service_approval_task.delay(self.pk)

    def cancel(self):
        """
        Cancel a pending service update, or withdraw a current service
        from the directory.
        """
        previous_status = self.status
        self.status = Service.STATUS_CANCELED
        self.save()

        if previous_status == Service.STATUS_DRAFT:
            # TODO: Trigger JIRA ticket update saying the provider canceled their change
            pass
        elif previous_status == Service.STATUS_CURRENT:
            # TODO Trigger new JIRA ticket to notify staff that provider has withdrawn the service
            pass
