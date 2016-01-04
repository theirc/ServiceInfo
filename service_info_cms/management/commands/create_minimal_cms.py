from django.core.management.base import BaseCommand, CommandError
from email_user.models import EmailUser

from service_info_cms.utils import create_essential_pages


class Command(BaseCommand):
    help = """
        Create CMS pages which are required for basic functionality of the site.
        """

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('A single argument is required: user id for page publisher (e-mail)')
        publisher = EmailUser.objects.get(email=args[0])
        create_essential_pages(publisher)
