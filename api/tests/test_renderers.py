from csv import DictReader
from django.test import SimpleTestCase
from django.utils.translation import override

from api.renderers import CSVRenderer


class CSVRendererTestCase(SimpleTestCase):
    """CSV output for aggregate data."""

    def get_serializer_data(self, count=2):
        """Build dictionary matching the expected output of an aggregate serializer."""
        return [self.get_serializer_item(i) for i in range(count)]

    def get_serializer_item(self, number):
        """Single item result from the serializer output."""
        return {
            'url': 'http://example.com/resource/{}'.format(number),
            'number': number,
            'name_en': 'Thing {}'.format(number),
            'name_fr': 'La Thing {}'.format(number),
            'name_ar': '{} Thing'.format(number),
            'totals': [{
                'total': number + 1,
                'label_en': 'Label 1 en',
                'label_fr': 'Label 1 fr',
                'label_ar': 'Label 1 ar',
            }, {
                'total': number + 2,
                'label_en': 'Label 2 en',
                'label_fr': 'Label 2 fr',
                'label_ar': 'Label 2 ar',
            }, ],
        }

    def test_render(self):
        """Render in the default language."""
        data = self.get_serializer_data()
        result = CSVRenderer().render(data=data)
        resultreader = DictReader(result)
        for i, row in enumerate(resultreader):
            headers = ['Name', 'Label 1 en', 'Label 2 en']
            values = ['Thing {}'.format(i), str(i + 1), str(i + 2)]
            self.assertEqual(row, dict(zip(headers, values)))

    def test_render_other_language(self):
        """Render in a non-default language."""
        data = self.get_serializer_data()
        with override(language='fr'):
            result = CSVRenderer().render(data=data)
        resultreader = DictReader(result)
        for i, row in enumerate(resultreader):
            headers = ['Nom', 'Label 1 fr', 'Label 2 fr']
            values = ['La Thing {}'.format(i), str(i + 1), str(i + 2)]
            self.assertEqual(row, dict(zip(headers, values)))
