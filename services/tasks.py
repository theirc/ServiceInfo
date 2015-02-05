from celery.task import task
from django.contrib.sites.models import Site


@task
def email_provider_about_service_approval_task(service_pk):
    from services.models import Service
    service = Service.objects.get(pk=service_pk)
    context = {
        'site': Site.objects.get_current(),
        'service': service,
        'provider': service.provider,
        'user': service.provider.user,
    }
    # FIXME: choose user's preferred language before rendering the email
    service.provider.user.send_email_to_user(
        context,
        'email/service_approved_subject.txt',
        'email/service_approved_body.txt',
        'email/service_approved_body.html',
    )
