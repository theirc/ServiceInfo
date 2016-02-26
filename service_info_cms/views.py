import json
import logging

from cms.models.pagemodel import Page
from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponseServerError
from django.shortcuts import redirect
import requests

from .models import PageRating

GOOGLE_CAPTCHA_VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'

logger = logging.getLogger('__name__')


def verify_captcha(secret, response, remoteip=None):
    """
    From https://developers.google.com/recaptcha/docs/verify:
        secret: The shared key between your site and ReCAPTCHA.
        response: The user response token provided by the reCAPTCHA to the user
            and provided to your site on.
        remoteip (optional): The user's IP address.
    """
    post_data = {
        'secret': secret,
        'response': response,
    }
    if remoteip:
        post_data['remote'] = remoteip

    try:
        r = requests.post(
            GOOGLE_CAPTCHA_VERIFY_URL,
            data=post_data
        )
        if r.status_code != 200:
            logger.error('Google reCAPTCHA -> %d', r.status_code)
            return False
        # r.content (bytes) vs. r.text (str):
        #   JSON parsing requires str,
        #   logging of bytes is better because it will all be on one line
        #     (e.g., as b'{\n  "success": true\n}')
        logger.debug('Google reCAPTCHA -> %s', r.content)
        result = json.loads(r.text)
        if not result['success']:
            logger.error('Google reCAPTCHA -> %s', r.content)
            return False
    except Exception:
        logger.exception('Error fetching or parsing Google reCAPTCHA verification')
        return False

    return True


def update_page_rating(request):
    if request.method == 'POST':
        try:
            rating = int(request.POST['rating'])
            page_id = int(request.POST['page_id'])
            return_url = request.POST['return_url']
            recaptcha_response = request.POST['g-recaptcha-response']
        except (KeyError, ValueError):
            logger.exception('Error parsing POST arguments')
            return HttpResponseBadRequest('Invalid request')

        verified = verify_captcha(
            settings.CAPTCHA_SECRETKEY, recaptcha_response
        )

        if verified:
            page = Page.objects.get(pk=page_id)
            page_rating, created = PageRating.objects.get_or_create(page_obj=page)
            page_rating.update_rating_average(rating)
            return redirect(return_url)
        else:
            return HttpResponseServerError("reCAPTCHA validation error")

    return HttpResponseBadRequest('Invalid request')
