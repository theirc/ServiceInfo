import datetime

from django.conf import settings

from jira.client import JIRA


def get_jira():
    jira_kwargs = {
        'options': {'server': settings.JIRA_SERVER},
        'basic_auth': (settings.JIRA_USER, settings.JIRA_PASSWORD),
    }
    return JIRA(**jira_kwargs)


def default_newissue_kwargs():
    duedate = datetime.date.today() + datetime.timedelta(days=settings.JIRA_DUEIN_DAYS)
    return {
        'project': {'key': settings.JIRA_SERVICES_PROJECT_KEY},
        'issuetype': {'name': 'Task'},
        'duedate': str(duedate),
    }


def default_feedback_kwargs():
    duedate = datetime.date.today() + datetime.timedelta(days=settings.JIRA_DUEIN_DAYS)
    return {
        'project': {'key': settings.JIRA_FEEDBACK_PROJECT_KEY},
        'issuetype': {'name': 'Task'},
        'duedate': str(duedate),
    }


def default_request_for_service_kwargs():
    duedate = datetime.date.today() + datetime.timedelta(days=settings.JIRA_DUEIN_DAYS)
    return {
        'project': {'key': settings.JIRA_REQUEST_SERVICE_PROJECT_KEY},
        'issuetype': {'name': 'Task'},
        'duedate': str(duedate),
    }
