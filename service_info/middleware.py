from .urls import NO_404_LOCALE_REDIRECTS

RESPONSE_ATTR = 'HiddenFromLocaleMiddleware'

# Wrap Hide404 and Restore404 around django.middleware.locale.LocaleMiddleware
# to bypass its 404 handling for paths matched in NO_404_LOCALE_REDIRECTS


class Hide404FromLocaleMiddleware(object):

    @staticmethod
    def process_response(request, response):
        if response.status_code == 404:
            for pattern in NO_404_LOCALE_REDIRECTS:
                if pattern.search(request.path_info):
                    setattr(response, RESPONSE_ATTR, True)
                    response.status_code = 409
                    break
        return response


class Restore404AfterLocaleMiddleware(object):

    @staticmethod
    def process_response(request, response):
        if getattr(response, RESPONSE_ATTR, False):
            response.status_code = 404
            delattr(response, RESPONSE_ATTR)
        return response
