import os

from fabric.api import execute, local, task

PROJECT_NAME = "service_info"
PROJECT_ROOT = os.path.dirname(__file__)
CONF_ROOT = os.path.join(PROJECT_ROOT, 'conf')


@task
def build():
    local("gulp build")


@task
def makemessages():
    """
    Find all the translatable English messages in our source and
    pull them out into locale/en/LC_MESSAGES/django.po
    """
    local("python manage.py makemessages --ignore 'conf/*' --ignore 'docs/*' "
          "--ignore 'requirements/*' --ignore 'frontend/*' "
          "--ignore 'node_modules/*' "
          "--no-location --no-obsolete "
          "-l en")
    local("i18next-conv -s frontend/locales/en/translation.json -t "
          "locale/en/LC_MESSAGES/frontend.po -l en")


@task
def pushmessages():
    """
    Upload the latest locale/en/LC_MESSAGES/django.po to Transifex
    """
    local("tx push -s")


@task
def pullmessages():
    """
    Pull the latest locale/ar/LC_MESSAGES/django.po and
    locale/fr/LC_MESSAGES/django.po from Transifex.

    Then take the updated frontend.po files and update the
    french and arabic translation.json files.
    """
    local("tx pull -af")
    for lang in ('fr', 'ar'):
        local("i18next-conv "
              " -t frontend/locales/%(lang)s/translation.json"
              " -s locale/%(lang)s/LC_MESSAGES/frontend.po"
              " -l %(lang)s" % locals())
    execute(compilemessages)


@task
def compilemessages():
    """
    Compile all the .po files into the .mo files that Django
    will get translated messages from at runtime.
    """
    local("python manage.py compilemessages -l en -l ar -l fr")
