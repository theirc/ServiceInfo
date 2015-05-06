from collections import defaultdict
from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db.transaction import atomic
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _, get_language

from . import jira_support
from .tasks import email_provider_about_service_approval_task
from .utils import absolute_url


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

    def __str__(self):
        return self.name


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

    def get_api_url(self):
        """Return the PATH part of the URL to access this object using the API"""
        return reverse('providertype-detail', args=[self.id])


def blank_or_at_least_one_letter(s):
    return s == '' or any([c.isalpha() for c in s])


class Provider(NameInCurrentLanguageMixin, models.Model):
    name_en = models.CharField(
        # Translators: Provider name
        _("name in English"),
        max_length=256,  # Length is a guess
        default='',
        blank=True,
        validators=[blank_or_at_least_one_letter]
    )
    name_ar = models.CharField(
        # Translators: Provider name
        _("name in Arabic"),
        max_length=256,  # Length is a guess
        default='',
        blank=True,
        validators=[blank_or_at_least_one_letter]
    )
    name_fr = models.CharField(
        # Translators: Provider name
        _("name in French"),
        max_length=256,  # Length is a guess
        default='',
        blank=True,
        validators=[blank_or_at_least_one_letter]
    )
    type = models.ForeignKey(
        ProviderType,
        verbose_name=_("type"),
    )
    phone_number = models.CharField(
        _("phone number"),
        max_length=20,
        validators=[
            RegexValidator(settings.PHONE_NUMBER_REGEX)
        ]
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
        blank=True, null=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1000000)
        ]
    )
    focal_point_name_en = models.CharField(
        _("focal point name in English"),
        max_length=256,  # Length is a guess
        default='',
        blank=True,
        validators=[blank_or_at_least_one_letter]
    )
    focal_point_name_ar = models.CharField(
        _("focal point name in Arabic"),
        max_length=256,  # Length is a guess
        default='',
        blank=True,
        validators=[blank_or_at_least_one_letter]
    )
    focal_point_name_fr = models.CharField(
        _("focal point name in French"),
        max_length=256,  # Length is a guess
        default='',
        blank=True,
        validators=[blank_or_at_least_one_letter]
    )
    focal_point_phone_number = models.CharField(
        _("focal point phone number"),
        max_length=20,
        validators=[
            RegexValidator(settings.PHONE_NUMBER_REGEX)
        ]
    )
    address_en = models.TextField(
        _("provider address in English"),
        default='',
        blank=True,
    )
    address_ar = models.TextField(
        _("provider address in Arabic"),
        default='',
        blank=True,
    )
    address_fr = models.TextField(
        _("provider address in French"),
        default='',
        blank=True,
    )

    def get_api_url(self):
        """Return the PATH part of the URL to access this object using the API"""
        return reverse('provider-detail', args=[self.id])

    def get_fetch_url(self):
        """Return the PATH part of the URL to fetch this object using the API"""
        return reverse('provider-fetch', args=[self.id])

    def notify_jira_of_change(self):
        JiraUpdateRecord.objects.create(
            update_type=JiraUpdateRecord.PROVIDER_CHANGE,
            provider=self
        )

    def get_admin_edit_url(self):
        """Return the PATH part of the URL to edit this object in the admin"""
        return reverse('admin:services_provider_change', args=[self.id])


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
    service = models.ForeignKey('services.Service', related_name='selection_criteria')

    class Meta(object):
        verbose_name_plural = _("selection criteria")

    def clean(self):
        if not any([self.text_en, self.text_fr, self.text_ar]):
            raise ValidationError(_("Selection criterion must have text in at least "
                                    "one language"))

    def __str__(self):
        return ', '.join([text for text in [self.text_en, self.text_ar, self.text_fr] if text])

    def get_api_url(self):
        return reverse('selectioncriterion-detail', args=[self.id])


class ServiceType(NameInCurrentLanguageMixin, models.Model):
    number = models.IntegerField(unique=True)
    icon = models.ImageField(
        upload_to='service-type-icons',
        verbose_name=_("icon"),
        blank=True,
    )
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

    def get_api_url(self):
        return reverse('servicetype-detail', args=[self.id])

    def get_icon_url(self):
        """Return URL PATH of the icon image for this record"""
        # For convenience of serializers
        if self.icon:
            return self.icon.url


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

    # Note: we don't let multiple non-archived versions of a service record pile up
    # there should be no more than two, one in current status and/or one in some other
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
        help_text=_('If a service record represents a modification of another service '
                    'record, this field links to that other record.'),
        null=True,
        blank=True,
        related_name='updates',
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

    objects = models.GeoManager()

    def get_api_url(self):
        return reverse('service-detail', args=[self.id])

    def get_provider_fetch_url(self):
        # For convenience of the serializer
        return self.provider.get_fetch_url()

    def get_admin_edit_url(self):
        return reverse('admin:services_service_change', args=[self.id])

    def email_provider_about_approval(self):
        """Schedule a task to send an email to the provider"""
        email_provider_about_service_approval_task.delay(self.pk)

    def may_approve(self):
        return self.status == self.STATUS_DRAFT

    def may_reject(self):
        return self.status == self.STATUS_DRAFT

    def cancel(self):
        """
        Cancel a pending service update, or withdraw a current service
        from the directory.
        """
        # First cancel any pending changes to this service
        for pending_change in self.updates.filter(status=Service.STATUS_DRAFT):
            pending_change.cancel()

        previous_status = self.status
        self.status = Service.STATUS_CANCELED
        self.save()

        if previous_status == Service.STATUS_DRAFT:
            JiraUpdateRecord.objects.create(
                service=self,
                update_type=JiraUpdateRecord.CANCEL_DRAFT_SERVICE)
        elif previous_status == Service.STATUS_CURRENT:
            JiraUpdateRecord.objects.create(
                service=self,
                update_type=JiraUpdateRecord.CANCEL_CURRENT_SERVICE)

    def save(self, *args, **kwargs):
        new_service = self.pk is None
        superseded_draft = None

        with atomic():  # All or none of this
            if (new_service
                    and self.status == Service.STATUS_DRAFT
                    and self.update_of
                    and self.update_of.status == Service.STATUS_DRAFT):
                # Any edit of a record that's still in review means we're
                # superseding one draft with another.
                superseded_draft = self.update_of
                # Bump this one up a level - we're replacing a pending change.
                self.update_of = superseded_draft.update_of

            super().save(*args, **kwargs)

            if new_service:
                # Now we've safely saved this new record.
                # Did we replace an existing draft? Archive the previous one.
                if superseded_draft:
                    superseded_draft.status = Service.STATUS_ARCHIVED
                    superseded_draft.save()
                    JiraUpdateRecord.objects.create(
                        service=self,
                        superseded_draft=superseded_draft,
                        update_type=JiraUpdateRecord.SUPERSEDED_DRAFT)
                elif self.update_of:
                    # Submitted a proposed change to an existing service
                    JiraUpdateRecord.objects.create(
                        service=self,
                        update_type=JiraUpdateRecord.CHANGE_SERVICE)
                else:
                    # Submitted a new service
                    JiraUpdateRecord.objects.create(
                        service=self,
                        update_type=JiraUpdateRecord.NEW_SERVICE)

    def validate_for_approval(self):
        """
        Raise a ValidationError if this service's data doesn't look valid to
        be a current, approved service.

        Current checks:

        * self.full_clean()
        * .location must be set
        * at least one language field for each of several translated fields must be set
        * status must be DRAFT
        """
        try:
            self.full_clean()
        except ValidationError as e:
            errs = e.error_dict
        else:
            errs = {}
        if not self.location:
            errs['location'] = [_('This field is required.')]
        for field in ['name', 'description']:
            if not any([getattr(self, '%s_%s' % (field, lang)) for lang in ['en', 'ar', 'fr']]):
                errs[field] = [_('This field is required.')]
        if self.status != Service.STATUS_DRAFT:
            errs['status'] = [_('Only services in draft status may be approved.')]
        if errs:
            raise ValidationError(errs)

    def staff_approve(self, staff_user):
        """
        Staff approving the service (new or changed).

        :param staff_user: The user who approved
        :raises: ValidationErrror
        """
        # Make sure it's ready
        self.validate_for_approval()
        # if there's already a current record, archive it
        if self.update_of and self.update_of.status == Service.STATUS_CURRENT:
            self.update_of.status = Service.STATUS_ARCHIVED
            self.update_of.save()
        self.status = Service.STATUS_CURRENT
        self.save()
        self.email_provider_about_approval()
        JiraUpdateRecord.objects.create(
            service=self,
            update_type=JiraUpdateRecord.APPROVE_SERVICE,
            by=staff_user
        )

    def validate_for_rejecting(self):
        """
        Raise a ValidationError if this service's data doesn't look valid to
        be rejected.

        Current checks:

        * self.full_clean()
        * status must be DRAFT
        """
        try:
            self.full_clean()
        except ValidationError as e:
            errs = e.error_dict
        else:
            errs = {}
        if self.status != Service.STATUS_DRAFT:
            errs['status'] = [_('Only services in draft status may be rejected.')]
        if errs:
            raise ValidationError(errs)

    def staff_reject(self, staff_user):
        """
        Staff rejecting the service (new or changed)

        :param staff_user: The user who rejected
        """
        # Make sure it's ready
        self.validate_for_rejecting()
        self.status = Service.STATUS_REJECTED
        self.save()
        JiraUpdateRecord.objects.create(
            service=self,
            update_type=JiraUpdateRecord.REJECT_SERVICE,
            by=staff_user
        )

    @property
    def longitude(self):
        if self.location:
            return self.location[0]

    @longitude.setter
    def longitude(self, value):
        if self.location is None:
            self.location = Point(0, 0)
        self.location[0] = value

    @property
    def latitude(self):
        if self.location:
            return self.location[1]

    @latitude.setter
    def latitude(self, value):
        if self.location is None:
            self.location = Point(0, 0)
        self.location[1] = value


class JiraUpdateRecord(models.Model):
    service = models.ForeignKey(Service, blank=True, null=True, related_name='jira_records')
    superseded_draft = models.ForeignKey(Service, blank=True, null=True)
    provider = models.ForeignKey(Provider, blank=True, null=True, related_name='jira_records')
    feedback = models.ForeignKey(
        'services.Feedback', blank=True, null=True, related_name='jira_records')
    PROVIDER_CHANGE = 'provider-change'
    NEW_SERVICE = 'new-service'
    CHANGE_SERVICE = 'change-service'
    CANCEL_DRAFT_SERVICE = 'cancel-draft-service'
    CANCEL_CURRENT_SERVICE = 'cancel-current-service'
    SUPERSEDED_DRAFT = 'superseded-draft'
    APPROVE_SERVICE = 'approve-service'
    REJECT_SERVICE = 'rejected-service'
    FEEDBACK = 'feedback'
    UPDATE_CHOICES = (
        (PROVIDER_CHANGE, _('Provider updated their information')),
        (NEW_SERVICE, _('New service submitted by provider')),
        (CHANGE_SERVICE, _('Change to existing service submitted by provider')),
        (CANCEL_DRAFT_SERVICE, _('Provider canceled a draft service')),
        (CANCEL_CURRENT_SERVICE, _('Provider canceled a current service')),
        (SUPERSEDED_DRAFT, _('Provider superseded a previous draft')),
        (APPROVE_SERVICE, _('Staff approved a new or changed service')),
        (REJECT_SERVICE, _('Staff rejected a new or changed service')),
        (FEEDBACK, _('User submitted feedback')),
    )
    # Update types that indicate a new Service record was created
    NEW_SERVICE_RECORD_UPDATE_TYPES = [
        NEW_SERVICE, CHANGE_SERVICE, SUPERSEDED_DRAFT,
    ]
    # Update types that indicate a draft or service is being canceled/deleted
    END_SERVICE_UPDATE_TYPES = [
        CANCEL_DRAFT_SERVICE, CANCEL_CURRENT_SERVICE,
    ]
    STAFF_ACTION_SERVICE_UPDATE_TYPES = [
        APPROVE_SERVICE, REJECT_SERVICE
    ]
    SERVICE_CHANGE_UPDATE_TYPES = (
        NEW_SERVICE_RECORD_UPDATE_TYPES + END_SERVICE_UPDATE_TYPES
        + STAFF_ACTION_SERVICE_UPDATE_TYPES
    )
    PROVIDER_CHANGE_UPDATE_TYPES = [
        PROVIDER_CHANGE,
    ]
    NEW_JIRA_RECORD_UPDATE_TYPES = [
        NEW_SERVICE, CHANGE_SERVICE, CANCEL_CURRENT_SERVICE, PROVIDER_CHANGE
    ]
    update_type = models.CharField(
        _('update type'),
        max_length=max([len(x[0]) for x in UPDATE_CHOICES]),
        choices=UPDATE_CHOICES,
    )
    jira_issue_key = models.CharField(
        _("JIRA issue"),
        max_length=256,
        blank=True,
        default='')
    by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
    )

    class Meta(object):
        # The service udpate types can each only happen once per service
        unique_together = (('service', 'update_type'),)

    def save(self, *args, **kwargs):
        errors = []
        is_new = self.pk is None
        if self.update_type == '':
            errors.append('must have a non-blank update_type')
        elif self.update_type == self.FEEDBACK:
            if not self.feedback:
                errors.append("%s must specify feedback' % self.update_type")
        elif self.update_type in self.PROVIDER_CHANGE_UPDATE_TYPES:
            if not self.provider:
                errors.append('%s must specify provider' % self.update_type)
            if self.service:
                errors.append('%s must not specify service' % self.update_type)
        elif self.update_type in self.SERVICE_CHANGE_UPDATE_TYPES:
            if self.service:
                if self.update_type == self.NEW_SERVICE and self.service.update_of:
                    errors.append('%s must not specify a service that is an update of another'
                                  % self.update_type)
                # If we're not creating a new record, be more tolerant; the service might
                # have been updated one way or another.
                if (is_new and self.update_type == self.CHANGE_SERVICE
                        and not self.service.update_of):
                    errors.append('%s must specify a service that is an update of another'
                                  % self.update_type)
            else:
                errors.append('%s must specify service' % self.update_type)
            if self.provider:
                errors.append('%s must not specify provider' % self.update_type)
            if self.update_type == self.SUPERSEDED_DRAFT and not self.superseded_draft:
                errors.append('%s must specifiy superseded draft service')
        else:
            errors.append('unrecognized update_type: %s' % self.update_type)
        if self.update_type in self.STAFF_ACTION_SERVICE_UPDATE_TYPES:
            if not self.by:
                errors.append('%s must specify user in "by" field')

        if errors:
            raise Exception('%s cannot be saved: %s' % (str(self), ', '.join(e for e in errors)))
        super().save(*args, **kwargs)

    def do_jira_work(self, jira=None):
        sentinel_value = 'PENDING'
        # Bail out early if we don't yet have a pk, if we already have a JIRA
        # issue key set, or if some other thread is already working on getting
        # an issue created/updated.
        if not self.pk or JiraUpdateRecord.objects.filter(pk=self.pk, jira_issue_key='').update(
                jira_issue_key=sentinel_value) != 1:
            return

        try:
            if not jira:
                jira = jira_support.get_jira()

            if self.update_type in JiraUpdateRecord.NEW_JIRA_RECORD_UPDATE_TYPES:
                kwargs = jira_support.default_newissue_kwargs()
                service = None
                service_url = None
                change_type = {
                    JiraUpdateRecord.NEW_SERVICE: 'New service',
                    JiraUpdateRecord.CHANGE_SERVICE: 'Changed service',
                    JiraUpdateRecord.CANCEL_CURRENT_SERVICE: 'Canceled service',
                    JiraUpdateRecord.PROVIDER_CHANGE: 'Changed provider',
                }[self.update_type]
                if self.update_type in JiraUpdateRecord.SERVICE_CHANGE_UPDATE_TYPES:
                    service = self.service
                    service_url = absolute_url(service.get_admin_edit_url())
                    provider = self.service.provider
                elif self.update_type in self.PROVIDER_CHANGE_UPDATE_TYPES:
                    provider = self.provider
                kwargs['summary'] = '%s from %s' % (change_type, provider)
                template_name = {
                    JiraUpdateRecord.NEW_SERVICE: 'jira/new_service.txt',
                    JiraUpdateRecord.CHANGE_SERVICE: 'jira/changed_service.txt',
                    JiraUpdateRecord.CANCEL_CURRENT_SERVICE: 'jira/canceled_service.txt',
                    JiraUpdateRecord.PROVIDER_CHANGE: 'jira/changed_provider.txt',
                }[self.update_type]
                context = {
                    'site': Site.objects.get_current(),
                    'provider': provider,
                    'provider_url': absolute_url(provider.get_admin_edit_url()),
                    'service': service,
                    'service_url': service_url,
                }
                if service and service.update_of:
                    context['service_parent_url'] = \
                        absolute_url(service.update_of.get_admin_edit_url())
                kwargs['description'] = render_to_string(template_name, context)
                new_issue = jira.create_issue(**kwargs)
                self.jira_issue_key = new_issue.key
                self.save()
            elif self.update_type == self.SUPERSEDED_DRAFT:
                # Track down the issue that's already been created so we
                # can comment on it.
                previous_record = JiraUpdateRecord.objects.get(service=self.superseded_draft)
                issue_key = previous_record.jira_issue_key
                context = {
                    'service': self.service,
                    'service_url': absolute_url(self.service.get_admin_edit_url()),
                }
                comment = render_to_string('jira/superseded_draft.txt', context)
                jira.add_comment(issue_key, comment)
                self.jira_issue_key = issue_key
                self.save()
            elif self.update_type == self.CANCEL_DRAFT_SERVICE:
                # Track down the issue that's already been created so we
                # can comment on it.
                previous_record = JiraUpdateRecord.objects.get(
                    update_type__in=JiraUpdateRecord.NEW_SERVICE_RECORD_UPDATE_TYPES,
                    service=self.service
                )
                issue_key = previous_record.jira_issue_key
                comment = 'Pending draft change was canceled by the provider.'
                jira.add_comment(issue_key, comment)
                self.jira_issue_key = issue_key
                self.save()
            elif self.update_type in self.STAFF_ACTION_SERVICE_UPDATE_TYPES:
                # Track down the issue that's already been created so we
                # can comment on it.
                previous_record = JiraUpdateRecord.objects.get(
                    update_type__in=JiraUpdateRecord.NEW_SERVICE_RECORD_UPDATE_TYPES,
                    service=self.service
                )
                issue_key = previous_record.jira_issue_key
                messages = {
                    (self.NEW_SERVICE, self.APPROVE_SERVICE):
                        "The new service was approved by %s.",
                    (self.NEW_SERVICE, self.REJECT_SERVICE):
                        "The new service was rejected by %s.",
                    (self.CHANGE_SERVICE, self.APPROVE_SERVICE):
                        "The service change was approved by %s.",
                    (self.CHANGE_SERVICE, self.REJECT_SERVICE):
                        "The service change was rejected by %s.",
                }
                comment = messages.get((previous_record.update_type, self.update_type),
                                       "The service's state was updated by %s.")
                comment = comment % self.by.email
                jira.add_comment(issue_key, comment)
                self.jira_issue_key = issue_key
                self.save()
            elif self.update_type == self.FEEDBACK:
                kwargs = jira_support.default_feedback_kwargs()
                kwargs['summary'] = 'Feedback about %s' % (self.feedback.service,)
                context = {
                    'site': Site.objects.get_current(),
                    'feedback': self.feedback,
                    'service': self.feedback.service,
                    'service_url': absolute_url(self.feedback.service.get_admin_edit_url()),
                    'provider': self.feedback.service.provider,
                }
                template_name = 'jira/feedback.txt'
                kwargs['description'] = render_to_string(template_name, context)
                new_issue = jira.create_issue(**kwargs)
                self.jira_issue_key = new_issue.key
                self.save()

        finally:
            # If we've not managed to save a valid JIRA issue key, reset value to
            # empty string so it'll be tried again later.
            JiraUpdateRecord.objects.filter(pk=self.pk, jira_issue_key=sentinel_value).update(
                jira_issue_key='')


#
# FEEDBACK
#
class Nationality(NameInCurrentLanguageMixin, models.Model):
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

    class Meta:
        verbose_name_plural = _("nationalities")

    def get_api_url(self):
        return reverse('nationality-detail', args=[self.id])


class Feedback(models.Model):
    # About the user
    name = models.CharField(
        _("name"),
        max_length=256
    )
    phone_number = models.CharField(
        _("phone number"),
        max_length=20,
        validators=[
            RegexValidator(settings.PHONE_NUMBER_REGEX)
        ]
    )
    nationality = models.ForeignKey(
        verbose_name=_("nationality"),
        to=Nationality,
    )
    area_of_residence = models.ForeignKey(
        ServiceArea,
        verbose_name=_("area of residence"),
    )

    # The service getting feedback
    service = models.ForeignKey(
        verbose_name=_("service"),
        to=Service,
    )

    # Questions about delivery of service
    delivered = models.BooleanField(
        help_text=_("Was the service you sought delivered to you?"),
        default=False,  # Don't really want a default here, but Django screams at you
    )
    quality = models.SmallIntegerField(
        help_text=_("How would you rate the quality of the service you received (from 1 to 5, "
                    "where 5 is the highest rating possible)?"),
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ],
        default=None,
        blank=True,
        null=True,
    )
    non_delivery_explained = models.CharField(
        # This is required only if 'delivered' is false; so needs to be optional here
        # and we'll validate that elsewhere
        help_text=_("Did you receive a clear explanation for why the service you "
                    "sought was not delivered to you?"),
        blank=True,
        default=None,
        null=True,
        max_length=8,
        choices=[
            ('no', _("No explanation")),
            ('unclear', _("Explanation was not clear")),
            ('unfair', _("Explanation was not fair")),
            ('yes', _("Clear and appropriate explanation")),
        ]
    )
    wait_time = models.CharField(
        # Presumably, only required if 'delivered' is true
        help_text=_("How long did you wait for the service to be delivered, after "
                    "contacting the service provider?"),
        blank=True,
        null=True,
        default=None,
        max_length=12,
        choices=[
            ('lesshour', _("Less than 1 hour")),
            ('uptotwodays', _("1-48 hours")),
            ('3-7days', _("3-7 days")),
            ('1-2weeks', _("1-2 weeks")),
            ('more', _("More than 2 weeks")),
        ]
    )
    wait_time_satisfaction = models.SmallIntegerField(
        help_text=_("How do you rate your satisfaction with the time that you waited for "
                    "the service to be delivered (from 1 to 5, where 5 is the highest "
                    "rating possible)?"),
        default=None,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )

    difficulty_contacting = models.CharField(
        help_text=_("Did you experience difficulties contacting the provider of "
                    "the service you needed?"),
        max_length=20,
        choices=[
            ('no', _("No")),
            ('didntknow', _("Did not know how to contact them")),
            ('nophoneresponse', _("Tried to contact them by phone but received no response")),
            ('noresponse', _("Tried to contact them in person but received no response or "
                             "did not find their office")),
            ('unhelpful', _("Contacted them but response was unhelpful")),
            ('other', _("Other")),
        ]
    )
    other_difficulties = models.TextField(
        # Only if 'other' selected above
        help_text=_("Other difficulties contacting the service provider"),
        blank=True,
        default='',
    )
    staff_satisfaction = models.SmallIntegerField(
        help_text=_("How would you rate your satisfaction with the staff of the organization "
                    "that provided services to you, (from 1 to 5, where 5 is the highest "
                    "rating possible)?"),
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    extra_comments = models.TextField(
        help_text=_("Other comments"),
        default='',
        blank=True,
    )
    anonymous = models.BooleanField(
        help_text=_("I want my feedback to be anonymous to the service provider"),
        default=False,
    )

    def clean(self):
        errs = defaultdict(list)
        if self.delivered:
            if self.quality is None:
                errs['quality'].append(
                    _("Quality field is required if you answered 'Yes' to "
                      "'Was the service you sought delivered to you?'."))
            if self.wait_time is None:
                errs['wait_time'].append(
                    _("An answer is required to 'How long did you wait for the service to "
                      "be delivered, after contacting the service provider?' "
                      "if you answered 'Yes' to "
                      "'Was the service you sought delivered to you?'."))
            if self.wait_time_satisfaction is None:
                errs['wait_time_satisfaction'].append(
                    _("An answer is required to 'How do you rate your satisfaction with the "
                      "time that you waited for the service to be delivered?' "
                      "if you answered 'Yes' to "
                      "'Was the service you sought delivered to you?'.")
                )
        else:
            if self.non_delivery_explained is None:
                errs['non_delivery_explained'].append(
                    _("An answer is required to 'Did you receive a clear explanation for "
                      "why the service you sought was not delivered to you?' "
                      "if you answered 'No' to "
                      "'Was the service you sought delivered to you?'."))
        if self.difficulty_contacting == 'other':
            if not self.other_difficulties:
                errs['other_difficulties'].append(
                    _("An answer is required to 'Other difficulties contacting the service "
                      "provider' "
                      "if you answered 'Other' to 'Did you experience difficulties contacting "
                      "the provider of the service you needed?'")
                )

        if errs:
            raise ValidationError(errs)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.pk:
            JiraUpdateRecord.objects.create(
                feedback=self,
                update_type=JiraUpdateRecord.FEEDBACK
            )
