from cms.api import create_page, create_title, publish_page
from cms.models import Page
from django.conf import settings


def create_essential_pages(page_publisher):
    languages = [entry[0] for entry in settings.LANGUAGES]

    if not Page.objects.count():
        create_page(
            title='Home',
            template='cms/content-types/homepage.html',
            language=languages[0],
            published=True
        )
        # Having the Home page in all languages is not essential.

    if not Page.objects.filter(reverse_id='search-results').exists():
        search_page = create_page(
            title='Search',
            template='cms/content-types/page.html',
            language=languages[0],
            apphook='AldrynSearchApphook',
            reverse_id='search-results',
            published=True
        )
        # The search results page must exist in all languages.
        for lang in languages[1:]:
            create_title(language=lang, title='Search', page=search_page)
            publish_page(page=search_page, user=page_publisher, language=lang)
