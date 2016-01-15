import io
import re

from django.test import TestCase
from django.core import management


EXPECTED_CHANGES = {
    'aldryn_faq': [
        # Py3K-izing default=b'{}', which is interpreted with encoding UTF-8
        # migrations.AlterField(
        #     model_name='faqconfig',
        #     name='app_data',
        #     field=app_data.fields.AppDataField(default=b'{}', editable=False),
        '- Alter field app_data on faqconfig',
    ],
}


class MissingMigrationTestCase(TestCase):

    def test(self):
        state = 'I'  # 'I' == initial, 'R' == reading changes for module
        actual_changes = []
        module = ''
        actual_modules = []
        with io.StringIO() as f:
            management.call_command('makemigrations', dry_run=True, stdout=f, no_color=True)
            f.seek(0)
            while True:
                l = f.readline()
                if l in ('', 'No changes detected'):
                    break
                if l.startswith('Migrations'):
                    if state != 'I':
                        self.assertEqual(EXPECTED_CHANGES[module], actual_changes)
                    state = 'R'
                    module = re.match(r'^Migrations for \'(.+)\'', l).group(1)
                    actual_modules.append(module)
                elif re.search(r'^ +.*\.py:', l):
                    continue
                else:
                    self.assertTrue(state == 'R')
                    actual_changes.append(l.strip())
        if state != 'I':
            self.assertEqual(EXPECTED_CHANGES[module], actual_changes)
        self.assertEqual(sorted(EXPECTED_CHANGES.keys()), sorted(actual_modules))
