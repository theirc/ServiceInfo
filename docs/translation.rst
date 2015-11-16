Translation
===========

Backend
-------

Backend translation uses the standard Django translation mechanisms
(https://docs.djangoproject.com/en/1.7/topics/i18n/).

Then we use Transifex to make it easy for client staff to provide
translations of the text in the Django project.

Frontend
--------

Frontend translation uses
`i18next-client <http://i18next.com/pages/doc_init.html>`_.
The source messages are in
``frontend/locales/en/translation.json``.

Our fab helper commands convert those to `*.po` files and
push them to Transifex for translation, then convert the
translated .po files to json for i18next-client to use.

Adding features and fixing bugs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

While the ``.po`` files can be regenerated easily by running
``fab makemessages`` again for English or ``fab pullmessages``
for the translated languages, we still store them in Git to
make it easier to keep an eye on changes, and maybe revert
if we have to.  (That way we are less likely to accidentally
make a mistake and delete huge swaths of messages and not
even notice it.)

We also store the ``.mo`` files because those are what Django gets the
translated messages from at runtime.

Updating messages on Transifex
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Anytime there have been changes to the messages in the code or templates
that have been merged to develop, someone should update the messages on
Transifex as follows:

1. Make sure you have the latest code from develop::

    git checkout develop
    git pull

#. regenerate the English (only) .po files::

    fab makemessages

#. Run "git diff" and make sure the changes look reasonable.

#. If so, commit the updated .po file to develop and push it
   upstream::

       git commit -m "Updated messages" locale/en/LC_MESSAGES/*.po
       git push

   (Commiting the .po files isn't strictly necessary since we can recreate
   it, but we can tell what's the latest version we pushed to Transifex
   by committing each version when we push it.)

#. push the updated source file to Transifex (http://support.transifex.com/customer/portal/articles/996211-pushing-new-translations)::

    fab pushmessages


Updating translations from Transifex
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Anytime translations on Transifex have been updated, someone should update
our translation files on the develop branch as follows:

1. Make sure you have the latest code from develop::

    git checkout develop
    git pull

#. pull the updated .po files from Transifex
   (http://support.transifex.com/customer/portal/articles/996157-getting-translations)::

    fab pullmessages

#. Use ``git diff`` to see if any translations have actually changed. If not, you
   can stop here.

#. Also look at the diffs to see if the changes look reasonable. E.g. if a whole lot
   of translations have vanished, figure out why before proceeding.

#. Compile the messages to .mo files::

    fab compilemessages

   If you get any errors due to badly formatted translations, open issues on
   Transifex and work with the translators to get them fixed, then start this
   process over.

#. Run your test suite one more time::

    python manage.py test

#. Commit and push the changes to github::

    git commit -m "Updated translations" locale/*/LC_MESSAGES/*.po locale/*/LC_MESSAGES/*.mo
    git push
