from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _, get_language


class ProviderType(models.Model):
    name_en = models.CharField(
        _("name in English"),
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
    name_ar = models.CharField(
        _("name in Arabic"),
        max_length=256,
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
        return reverse('providertype-detail', args=[self.id])


class Provider(models.Model):
    name = models.CharField(
        _("name"),
        max_length=256,  # Length is a guess
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
    description = models.TextField(
        _("description"),
    )
    user = models.OneToOneField(
        to=settings.AUTH_USER_MODEL,
        verbose_name=_('user'),
        help_text=_('user account for this provider'),
    )

    def __str__(self):
        return self.name

    def get_api_url(self):
        return reverse('provider-detail', args=[self.id])


class ServiceArea(models.Model):
    # FIXME: Find out what a "service area" consists of
    pass


class SelectionCriterion(models.Model):
    # FIXME: Find out what a "selection criterion" consists of
    pass  # ??

    class Meta(object):
        verbose_name_plural = _("selection criteria")


class Service(models.Model):
    provider = models.ForeignKey(
        Provider,
        verbose_name=_("provider"),
    )
    name = models.CharField(
        _("name"),
        max_length=256,
    )
    area_of_service = models.ForeignKey(
        ServiceArea,
        verbose_name=_("area of service"),
    )
    description = models.TextField(
        _("description"),
    )
    hours_of_service = models.TextField(  # FIXME: do we need to model these more specifically?
        _("hours of service"),
    )
    additional_info = models.TextField(
        _("additional info"),
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
        verbose_name=_("selection criteria"),
    )

    # Note: we don't let multiple versions of a service record pile up - there
    # should be no more than two, one in current status and/or one in some other
    # status.
    STATUS_DRAFT = 'draft'
    STATUS_CURRENT = 'current'
    STATUS_REJECTED = 'rejected'
    STATUS_CANCELED = 'canceled'
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

    def __str__(self):
        return self.name

    def get_api_url(self):
        return reverse('service-detail', args=[self.id])
