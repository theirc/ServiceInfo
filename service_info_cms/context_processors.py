from django.conf import settings


def captcha_key(request):
    return {'CAPTCHA_SITEKEY': settings.CAPTCHA_SITEKEY}
