import logging

from django.conf import settings
from django.contrib.sites.models import Site

from celery.task import task

from . import jira_support


logger = logging.getLogger(__name__)


@task
def email_provider_about_service_approval_task(service_pk):
    from .models import Service
    service = Service.objects.get(pk=service_pk)
    site = Site.objects.get_current()
    scheme = 'https' if settings.SECURE_LINKS else 'http'
    if settings.DEBUG:
        # E.g. http://localhost:8000/#/service/168
        service_link = '%s://%s/#/service/%d' % (scheme, site, service_pk)
    else:
        # E.g. https://serviceinfo-staging.rescue.org/app/#/service/22
        service_link = '%s://%s/app/#/service/%d' % (scheme, site, service_pk)
    context = {
        'site': site,
        'service': service,
        'provider': service.provider,
        'user': service.provider.user,
        'service_link': service_link,
    }
    service.provider.user.send_email_to_user(
        context,
        'email/service_approved_subject.txt',
        'email/service_approved_body.txt',
        'email/service_approved_body.html',
    )


@task
def process_jira_work():
    from .models import JiraUpdateRecord
    if not all((settings.JIRA_USER, settings.JIRA_PASSWORD, settings.JIRA_SERVER)):
        logger.error('JIRA configuration values are not all set, cannot do JIRA work.')
        return

    work_qs = JiraUpdateRecord.objects.order_by('id').filter(jira_issue_key='')
    todo_count = len(work_qs)
    done_count = 0

    if todo_count:
        jira = jira_support.get_jira()
        for jira_record in work_qs:
            jira_record.do_jira_work(jira)
            if jira_record.jira_issue_key:
                done_count += 1

    logger.info('process_jira_work successfully handled %s of %s pending work requests.' % (
        done_count, todo_count))
