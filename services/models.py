from django.db import models
from django.utils.translation import ugettext_lazy as _


class Provider(models.Model):
    # FIXME: Find out what the provider types are
    PROVIDER_TYPE_1 = 1
    PROVIDER_TYPE_2 = 2
    PROVIDER_TYPE_CHOICES = [
        (1, _("Provider type 1")),
        (2, _("Provider type 2")),
    ]

    name = models.CharField(
        _("name"),
        max_length=256,  # Length is a guess
    )
    type = models.IntegerField(
        _("type"),
        choices=PROVIDER_TYPE_CHOICES,
    )
    phone_number = models.CharField(
        _("phone number"),
        max_length=20,
    )
    email = models.EmailField(
        _("email"),
        blank=True,
        default='',
    )
    website = models.URLField(
        _("website"),
        blank=True,
        default='',
    )
    description = models.TextField(
        _("description"),
    )


class ServiceArea(models.Model):
    # FIXME: Find out what a "service area" consists of
    pass


class SelectionCriterion(models.Model):
    # FIXME: Find out what a "selection criterion" consists of
    pass  # ??


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
