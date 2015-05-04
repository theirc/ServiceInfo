from csv import writer
from io import StringIO

from django.utils.translation import get_language, ugettext as _

from rest_framework.renderers import BaseRenderer


class CSVRenderer(BaseRenderer):
    """Render aggregrate response data as a CSV."""

    media_type = 'text/csv'
    format = 'csv'
    charset = 'utf-8'
    render_style = 'text'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # FIXME: Initially these reports will have < 100 rows and < 10 columns
        # but it might not be a great idea to put this in memory
        lang = get_language()[:2]
        output = StringIO()
        outputwriter = writer(output)
        headers = None
        for result in data:
            totals = result['totals']
            if headers is None:
                headers = [_('Name'), ] + [t['label_{}'.format(lang)] for t in totals]
                outputwriter.writerow(headers)
            row = [result['name_{}'.format(lang)], ] + [t['total'] for t in totals]
            outputwriter.writerow(row)
        output.seek(0)
        return output
