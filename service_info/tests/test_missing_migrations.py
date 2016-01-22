import io
import re

from django.test import TestCase
from django.core import management

# By design, Django 1.7 migrations track various changes to models which don't
# affect the database schema, such as updates to field choices.  Some third-
# party packages have "missing migrations" when used in this project, usually
# triggered by different project settings which affect field choices or by
# Py 2.7 vs. Py3K nuances.
#
# The safe way to determine whether or not there is a problem is to generate
# the missing migrations in a temporary virtualenv then use the sqlmigrate
# command to ensure that they don't affect the database schema.
#
# Sample run:
#
# Migrations for 'aldryn_faq':
#   0011_auto_20160120_2019.py:
#     - Alter field app_data on faqconfig
# Migrations for 'email_notifications':
#   0002_auto_20160120_2019.py:
#     - Alter field theme on emailnotification
# Migrations for 'aldryn_newsblog':
#   0009_auto_20160120_2019.py:
#     - Alter field app_data on newsblogconfig
#     - Alter field template_prefix on newsblogconfig
# Migrations for 'aldryn_forms':
#   0005_auto_20160120_2019.py:
#     - Change Meta options on formsubmission
#     - Alter field email_body on emailfieldplugin
#     - Alter field email_send_notification on emailfieldplugin
#     - Alter field email_subject on emailfieldplugin
#     - Alter field language on formdata
#     - Alter field form_template on formplugin
#     - Alter field redirect_type on formplugin
#     - Alter field language on formsubmission
#
# $ python manage.py sqlmigrate aldryn_faq 0011
# $ python manage.py sqlmigrate email_notifications 0002
# $ python manage.py sqlmigrate aldryn_newsblog 0009
# $ python manage.py sqlmigrate aldryn_forms 0005
# $
#
# If this is a third-party package and the "missing" migration doesn't affect
# the db, then the package can be consumed as-is.

EXPECTED_CHANGES = {
    'aldryn_faq': [
        # Py3K-izing default=b'{}', which is interpreted with encoding UTF-8:
        # migrations.AlterField(
        #     model_name='faqconfig',
        #     name='app_data',
        #     field=app_data.fields.AppDataField(default='{}', editable=False),
        #     preserve_default=True,
        # ),
        '- Alter field app_data on faqconfig',
    ],
    'aldryn_forms': [
        # generates no SQL, detailed analysis is expected to be similar to
        # fields in other packages
        '- Change Meta options on formsubmission',
        '- Alter field email_body on emailfieldplugin',
        '- Alter field email_send_notification on emailfieldplugin',
        '- Alter field email_subject on emailfieldplugin',
        '- Alter field language on formdata',
        '- Alter field form_template on formplugin',
        '- Alter field redirect_type on formplugin',
        '- Alter field language on formsubmission',
    ],
    'aldryn_newsblog': [
        # newsblogconfig.app_data is same story as faqconfig.app_data above
        # migrations.AlterField(
        #     model_name='newsblogconfig',
        #     name='app_data',
        #     field=app_data.fields.AppDataField(default='{}', editable=False),
        #     preserve_default=True,
        # ),
        '- Alter field app_data on newsblogconfig',
        # Removing choices since choices has a different value since the last
        # time (now: [], before: [(b'dummy', b'dummy')])
        # migrations.AlterField(
        #     model_name='newsblogconfig',
        #     name='template_prefix',
        #     field=models.CharField(blank=True, verbose_name='Prefix for template dirs',
        #         max_length=20, null=True),
        #     preserve_default=True,
        # ),
        '- Alter field template_prefix on newsblogconfig',
    ],
    'email_notifications': [  # part of aldryn_forms package
        # Changing choices= because the project version has b'default' instead of 'default'
        # migrations.AlterField(
        #     model_name='emailnotification',
        #     name='theme',
        #     field=models.CharField(verbose_name='theme', choices=[('default', 'default')],
        #         help_text='Provides the base theme for the email.', max_length=200),
        #     preserve_default=True,
        # ),
        '- Alter field theme on emailnotification',
    ],
}


class MigrationCommandOutput(object):
    """Parse output from makemigrations command, generating a series of
      (module, changed_fields)"""

    INITIAL = 'INITIAL'
    READING = 'READING'  # reading changes for package

    def __init__(self, input_file):
        self.input = input_file

    def read(self):
        actual_changes = []
        module = ''
        state = self.INITIAL
        while True:
            l = self.input.readline()
            if l in ('', 'No changes detected'):
                break
            if l.startswith('Migrations'):
                if state != self.INITIAL:
                    yield module, actual_changes
                state = self.READING
                module = re.match(r'^Migrations for \'(.+)\'', l).group(1)
                actual_changes = []
            elif re.search(r'^ +.*\.py:', l):
                continue
            else:
                if state != self.READING:
                    raise ValueError('State is <%s> instead of <%s>' % (
                        state, self.READING
                    ))
                actual_changes.append(l.strip())
        if state != self.INITIAL:
            yield module, actual_changes


class MissingMigrationTestCase(TestCase):

    def test(self):
        actual_modules = []
        with io.StringIO() as f:
            management.call_command('makemigrations', dry_run=True, stdout=f, no_color=True)
            f.seek(0)
            migrations = MigrationCommandOutput(f)
            for module, actual_changes in migrations.read():
                actual_modules.append(module)
                self.assertEqual(EXPECTED_CHANGES[module], actual_changes)
        self.assertEqual(sorted(EXPECTED_CHANGES.keys()), sorted(actual_modules))
