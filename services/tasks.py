import logging

from django.conf import settings

from celery.task import task

from . import jira_support
from .models import JiraUpdateRecord


logger = logging.getLogger(__name__)


@task
def process_jira_work():

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
