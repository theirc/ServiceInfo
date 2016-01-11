from cms.menu import CMSMenu
from cms.models import Page
from menus.base import Modifier
from menus.menu_pool import menu_pool

# Menu nodes which represent real CMS Page objects (vs. some node
# synthesized by a CMS app, such as a "page" for items in a FAQ
# category) have this namespace.
CMS_PAGE_NODE_NAMESPACE = CMSMenu.__name__


class AddIconNameExtension(Modifier):
    """Make the IconNameExtension available in the menu."""

    def _modify_nodes(self, nodes):
        for node in nodes:
            if node.namespace == CMS_PAGE_NODE_NAMESPACE:
                page = Page.objects.get(pk=node.id)
                if getattr(page, 'iconnameextension', None):
                    setattr(node, 'iconnameextension', page.iconnameextension)
                self._modify_nodes(node.children)

    def modify(self, request, nodes, namespace, root_id, post_cut, breadcrumb):
        if post_cut and not breadcrumb:
            self._modify_nodes(nodes)
        return nodes


class AddRatingExtension(Modifier):
    """Make the RatingExtension available in the menu."""

    def _modify_nodes(self, nodes):
        for node in nodes:
            if node.namespace == CMS_PAGE_NODE_NAMESPACE:
                page = Page.objects.get(pk=node.id)
                if getattr(page, 'ratingextension', None):
                    setattr(node, 'iratingextension', page.ratingextension)
                self._modify_nodes(node.children)

    def modify(self, request, nodes, namespace, root_id, post_cut, breadcrumb):
        if post_cut and not breadcrumb:
            self._modify_nodes(nodes)
        return nodes


menu_pool.register_modifier(AddIconNameExtension)
menu_pool.register_modifier(AddRatingExtension)
