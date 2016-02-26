from cms.api import create_page, create_title, publish_page
from cms.models import Page, StaticPlaceholder
from django.conf import settings
from django.db import transaction


def create_essential_pages(page_publisher, site=None):
    languages = [entry[0] for entry in settings.LANGUAGES]

    if not Page.objects.count():
        create_page(
            title='Home',
            template='cms/content-types/homepage.html',
            language=languages[0],
            published=True,
            site=site
        )
        # Having the Home page in all languages is not essential.

    if not Page.objects.filter(reverse_id='search-results').exists():
        search_page = create_page(
            title='Search',
            template='cms/content-types/page.html',
            language=languages[0],
            apphook='AldrynSearchApphook',
            reverse_id='search-results',
            published=True,
            site=site
        )
        # The search results page must exist in all languages.
        for lang in languages[1:]:
            create_title(language=lang, title='Search', page=search_page)
            publish_page(page=search_page, user=page_publisher, language=lang)


def change_cms_site(from_site, to_site):
    pages = Page.objects.filter(site=from_site)
    placeholders = StaticPlaceholder.objects.filter(site=from_site)

    total_pages_moved = 0
    total_placeholders_moved = 0

    with transaction.atomic():
        for page in pages:
            page.site = to_site
            page.save()
            total_pages_moved += 1
        for placeholder in placeholders:
            placeholder.site = to_site
            placeholder.save()
            total_placeholders_moved += 1

    return total_pages_moved, total_placeholders_moved
