import io
import re

from django.test import TestCase
from django.core import management


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
            elif re.search(r'^ +.*\.py:', l):
                continue
            else:
                if state != self.READING:
                    raise ValueError('State is <%s> instead of <R>' % state)
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
