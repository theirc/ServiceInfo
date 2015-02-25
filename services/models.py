from textwrap import dedent
from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db.transaction import atomic
from django.utils.translation import ugettext_lazy as _, get_language

from . import jira_support
from .tasks import email_provider_about_service_approval_task


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
    )

    def __str__(self):
        return self.name_en

    def get_api_url(self):
        return reverse('provider-detail', args=[self.id])

    def notify_jira_of_change(self):
        JiraUpdateRecord.objects.create(
            update_type=JiraUpdateRecord.PROVIDER_CHANGE,
            provider=self
        )

    def get_admin_edit_url(self):
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

    def __str__(self):
        return ', '.join([self.text_en, self.text_fr, self.text_ar])

    def get_api_url(self):
        return reverse('selectioncriterion-detail', args=[self.id])


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
        help_text=_('If a service record represents a modification of an existing service '
                    'record that is still pending approval, this field links to the '
                    'existing service record.'),
        null=True,
        blank=True,
        related_name='pending_update',
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

    def __str__(self):
        return self.name_en

    def get_api_url(self):
        return reverse('service-detail', args=[self.id])

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

    def staff_approve(self):
        """
        Staff approving the service (new or changed)
        """
        # if there's already a current record, archive it
        if self.update_of and self.update_of.status == Service.STATUS_CURRENT:
            self.update_of.status = Service.STATUS_ARCHIVED
            self.update_of.save()
        self.status = Service.STATUS_CURRENT
        self.save()
        self.email_provider_about_approval()
        # FIXME: Trigger JIRA ticket update?

    def staff_reject(self):
        """
        Staff rejecting the service (new or changed)
        """
        self.status = Service.STATUS_REJECTED
        self.save()
        # FIXME: Trigger JIRA ticket update?


class JiraUpdateRecord(models.Model):
    service = models.ForeignKey(Service, blank=True, null=True, related_name='jira_records')
    superseded_draft = models.ForeignKey(Service, blank=True, null=True)
    provider = models.ForeignKey(Provider, blank=True, null=True, related_name='jira_records')
    PROVIDER_CHANGE = 'provider-change'
    NEW_SERVICE = 'new-service'
    CHANGE_SERVICE = 'change-service'
    CANCEL_DRAFT_SERVICE = 'cancel-draft-service'
    CANCEL_CURRENT_SERVICE = 'cancel-current-service'
    SUPERSEDED_DRAFT = 'superseded-draft'
    UPDATE_CHOICES = (
        (PROVIDER_CHANGE, _('Provider updated their information')),
        (NEW_SERVICE, _('New service submitted by provider')),
        (CHANGE_SERVICE, _('Change to existing service submitted by provider')),
        (CANCEL_DRAFT_SERVICE, _('Provider canceled a draft service')),
        (CANCEL_CURRENT_SERVICE, _('Provider canceled a current service')),
        (SUPERSEDED_DRAFT, _('Provider superseded a previous draft')),
    )
    # Update types that indicate a new Service record was created
    NEW_SERVICE_RECORD_UPDATE_TYPES = [
        NEW_SERVICE, CHANGE_SERVICE, SUPERSEDED_DRAFT,
    ]
    # Update types that indicate a draft or service is being canceled/deleted
    END_SERVICE_UPDATE_TYPES = [
        CANCEL_DRAFT_SERVICE, CANCEL_CURRENT_SERVICE,
    ]
    SERVICE_CHANGE_UPDATE_TYPES = NEW_SERVICE_RECORD_UPDATE_TYPES + END_SERVICE_UPDATE_TYPES
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

    class Meta(object):
        # The service udpate types can each only happen once per service
        unique_together = (('service', 'update_type'),)

    def save(self, *args, **kwargs):
        errors = []
        is_new = self.pk is None
        if self.update_type == '':
            errors.append('must have a non-blank update_type')
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
                change_type = {
                    JiraUpdateRecord.NEW_SERVICE: 'New service',
                    JiraUpdateRecord.CHANGE_SERVICE: 'Changed service',
                    JiraUpdateRecord.CANCEL_CURRENT_SERVICE: 'Canceled service',
                    JiraUpdateRecord.PROVIDER_CHANGE: 'Changed provider',
                }[self.update_type]
                if self.update_type in JiraUpdateRecord.SERVICE_CHANGE_UPDATE_TYPES:
                    url = self.service.get_admin_edit_url()
                    provider = self.service.provider
                elif self.update_type in self.PROVIDER_CHANGE_UPDATE_TYPES:
                    url = self.provider.get_admin_edit_url()
                    provider = self.provider
                kwargs['summary'] = '%s from %s' % (change_type, provider)
                kwargs['description'] = 'Details here:\nhttp://%s%s' % (
                    Site.objects.get_current(), url)
                new_issue = jira.create_issue(**kwargs)
                self.jira_issue_key = new_issue.key
                self.save()
            elif self.update_type == self.SUPERSEDED_DRAFT:
                # Track down the issue that's already been created so we
                # can comment on it.
                previous_record = JiraUpdateRecord.objects.get(service=self.superseded_draft)
                issue_key = previous_record.jira_issue_key
                link1 = 'http://%s%s' % (Site.objects.get_current(),
                                         self.superseded_draft.get_admin_edit_url())
                link2 = 'http://%s%s' % (Site.objects.get_current(),
                                         self.service.get_admin_edit_url())
                comment = dedent("""
                   The provider has updated a new service or a change that was still under review.
                   The previous data was at %s.
                   The new data is at %s.
                """ % (link1, link2))
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
                comment = 'Pending draft change was canceled by the provider'
                jira.add_comment(issue_key, comment)
                self.jira_issue_key = issue_key
                self.save()
        finally:
            # If we've not managed to save a valid JIRA issue key, reset value to
            # empty string so it'll be tried again later.
            JiraUpdateRecord.objects.filter(pk=self.pk, jira_issue_key=sentinel_value).update(
                jira_issue_key='')
