from http.client import OK
import logging
from django.conf import settings

from django.contrib.auth import get_user_model
from django.contrib.auth.views import logout
from django.core import signing
from django.core.signing import BadSignature
from django.http import HttpResponse, HttpResponseForbidden

from services.import_export import get_export_workbook_for_user


logger = logging.getLogger(__name__)


def export_view(request, signature):
    # Must have a valid signature that hasn't expired
    try:
        signed_value = signing.loads(signature, max_age=settings.SIGNED_URL_LIFETIME)
    except BadSignature:
        logger.exception("export signature validation failure")
        return HttpResponseForbidden('this signature is not valid')

    # what does this signature allow them to do?
    if signed_value.get('what', None) != 'export':
        return HttpResponseForbidden('this signature does not allow exports')

    # The signature's data contains the userid of the authenticated user
    # that the signature was given to
    user_id = signed_value.get('u', -1)
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error("User in export URL does not exist")
        return HttpResponseForbidden('this signature is not valid')

    response = HttpResponse(status=OK, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="service_info.xls"'

    book = get_export_workbook_for_user(user)
    book.save(response)

    return response

# Note: there's no Django view for imports. Those happen entirely
# through the API and methods in ./import_export.py in this package.


def health_view(request):
    return HttpResponse("I am okay.", content_type="text/plain")


def logout_view(request):
    return logout(request, next_page=settings.CMS_TOP)
