API
===

For the most part, the API uses the defaults of Django REST Framework
to provide access to the models in the usual way. You can browse
the API at `https://<yourserver>/api`.  This document will only
cover the little complications, like getting authenticated, creating
users, etc.

Authentication
--------------

TBD

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
