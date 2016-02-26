from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site

from service_info_cms.utils import change_cms_site


class Command(BaseCommand):
    """ Similar: cms/management/commands/subcommands/copy_site.py """

    help = 'Move the CMS pages from one site to another'
    args = '< --from original_site_domain --to new_site_domain | --list >'

    option_list = BaseCommand.option_list + (
        make_option('--from', default=None,
                    help='Domain of original site'),
        make_option('--to', default=None,
                    help='Domain of new site'),
        make_option('--list', default=None, action='store_true',
                    help='List available sites')
    )

    def handle(self, *args, **options):
        if options['list']:
            self.stdout.write('Available sites:')
            for site in Site.objects.all():
                self.stdout.write('  {0}\n'.format(site))
            return

        from_site_domain = options['from']
        to_site_domain = options['to']

        if not from_site_domain or not to_site_domain:
            raise CommandError('Use --list or specify both --from and --to arguments ')
        if from_site_domain == to_site_domain:
            raise CommandError('Original site and new site must be different')

        to_site = self.get_site(to_site_domain)
        from_site = self.get_site(from_site_domain)

        total_pages_moved, total_placeholders_moved = change_cms_site(from_site, to_site)
        self.stdout.write('Moved {0} pages from site {1} to site {2}.\n'.format(
            total_pages_moved, from_site_domain, to_site_domain
        ))
        self.stdout.write('Moved {0} static placeholders from site {1} to site {2}.\n'.format(
            total_placeholders_moved, from_site_domain, to_site_domain
        ))

    @staticmethod
    def get_site(domain):
        try:
            return Site.objects.get(domain=domain)
        except Site.DoesNotExist:
            raise CommandError('Unknown site: {0}'.format(domain))
