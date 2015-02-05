from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions, HTTP_HEADER_ENCODING


def get_service_info_authorization_header(request):
    """
    Return request's 'ServiceInfoAuthorization:' header, as a bytestring.

    Hide some test client ickyness where the header can be unicode.
    """
    auth = request.META.get('HTTP_SERVICEINFOAUTHORIZATION', b'')
    if isinstance(auth, type('')):
        # Work around django test client oddness
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth


class ServiceInfoTokenAuthentication(TokenAuthentication):

    def authenticate(self, request):
        auth = get_service_info_authorization_header(request).split()

        if not auth or auth[0].lower() != b'token':
            return None

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(auth[1])
