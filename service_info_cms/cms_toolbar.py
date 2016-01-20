from cms.toolbar_pool import toolbar_pool
from cms.extensions.toolbar import ExtensionToolbar
from django.utils.translation import ugettext_lazy as _
from .models import IconNameExtension, RatingExtension


# http://docs.django-cms.org/en/support-3.1.x/how_to/extending_page_title.html#simplified-toolbar-api
# with flake8 fix and different menu title
@toolbar_pool.register
class IconExtensionToolbar(ExtensionToolbar):
    # defines the model for the current toolbar
    model = IconNameExtension

    def populate(self):
        # setup the extension toolbar with permissions and sanity checks
        current_page_menu = self._setup_extension_toolbar()
        # if it's all ok
        if current_page_menu:
            # retrieves the instance of the current extension (if any) and the toolbar item url
            page_extension, url = self.get_page_extension_admin()
            if url:
                # adds a toolbar item
                current_page_menu.add_modal_item(
                    _('Set icon for page'), url=url, disabled=not self.toolbar.edit_mode)


@toolbar_pool.register
class RatingExtensionToolbar(ExtensionToolbar):
    model = RatingExtension

    def populate(self):
        current_page_menu = self._setup_extension_toolbar()
        if current_page_menu:
            page_extension, url = self.get_page_extension_admin()
            if url:
                current_page_menu.add_modal_item(
                    _('Allow ratings for page'), url=url, disabled=not self.toolbar.edit_mode)
