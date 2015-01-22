API
===

For the most part, the API uses the defaults of Django REST Framework
to provide access to the models in the usual way. You can browse
the API at `https://<yourserver>/api`.  This document will only
cover the little complications, like getting authenticated, creating
users, etc.

User activation
---------------

If the client has a user activation key, it can try to activate
the user by POSTing to '/api/activate/' with

    { 'activation_key': 'the key string' }

If successful, response status will be 200 and the response content will
include::

   { 'token': 'a long string'}

The token can be used to make subsequent API calls with the permissions
of that user (see below).

Otherwise, the response status will be 400 and the body might
contain::

    {'activation_key': ['Activation key is invalid or has already been used.']}
    {'activation_key': ['Activation link has expired.']}
    {'activation_key': ['Activation key is not a valid format. Make sure the activation link has been copied correctly.']}
    {'activation_key': ['This field may not be blank.']}

Login
-----

If a client has a user's email and password, it can get an auth
token and use that in subsequent calls.

POST to '/api/login/'::

   { 'email': 'email@example.com', 'password': 'plaintext password' }

If successful, response status will be 200 and the response
content will include::

   { 'token': 'a long string'}

If failed, response status will be 400 and the response might look like::

    {"non_field_errors":["Unable to log in with provided credentials."]}

or::

    {"email":["This field may not be blank."]}

or::

    {"non_field_errors":["User account is disabled."]}

Using token-based auth
----------------------

Once the client has the token, it should pass it on subsequent requests per
http://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication
which says::

    For clients to authenticate, the token key should be included in the
    Authorization HTTP header. The key should be prefixed by the string
    literal "Token", with whitespace separating the two strings. For example::

        Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b

As you might expect, requests will be permitted or denied based on the
permissions of the user whose token is passed.

Creating a new provider
-----------------------

The usual way to create a new instance of a model would be to POST
to the model's list URL. However, for new provider registration, it's
necessary to be able to create a new provider when not authenticated,
and the usual APIs don't allow that. So we've created a custom call
just for this.

To use it, POST to ``/api/provider/create_provider/``. The request data
is almost the same as it would be to create a Provider normally,
except instead of a 'user' field, it expects 'email' and 'passwword'
fields.

A new, inactive user will be created, and an email sent to the user with a
link they'll need to follow in order to activate their account.

Also, a new provider will be created for that user.
