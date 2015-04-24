from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from service_info.tests.test_frontend import ServiceInfoFrontendTestCase
from services.models import Service
from services.tests.factories import ServiceFactory


class SearchFrontendTest(ServiceInfoFrontendTestCase):

    def test_search_list_results_limited(self):
        """No more than 25 services in result"""
        for i in range(30):
            ServiceFactory(status=Service.STATUS_CURRENT)
        self.load_page_and_set_language()
        menu = self.wait_for_element('menu')
        search = menu.find_elements_by_link_text('Search')[0]
        search.click()
        self.wait_for_element('search_controls')
        self.assertHashLocation('/search')
        self.wait_for_element('.search-result-list > li', match=By.CSS_SELECTOR)
        results = self.browser.find_elements_by_css_selector('.search-result-list > li')
        self.assertEqual(25, len(results))

    def test_filtered_list_search(self):
        """Find services by type."""

        service = ServiceFactory(status=Service.STATUS_CURRENT)
        self.load_page_and_set_language()
        menu = self.wait_for_element('menu')
        search = menu.find_elements_by_link_text('Search')[0]
        search.click()
        form = self.wait_for_element('search_controls')
        self.assertHashLocation('/search')
        Select(form.find_element_by_name('type')).select_by_visible_text(
            service.type.name_en)
        controls = self.wait_for_element('map-toggle', match=By.CLASS_NAME)
        controls.find_element_by_name('map-toggle-list').click()
        try:
            result = self.wait_for_element('.search-result-list > li', match=By.CSS_SELECTOR)
            name = result.find_element_by_class_name('name')
        except StaleElementReferenceException:
            # Hit a race where we got a search element but then the page replaced it
            result = self.wait_for_element('.search-result-list > li', match=By.CSS_SELECTOR)
            name = result.find_element_by_class_name('name')
        self.assertEqual(name.text, service.name_en)

    def test_localized_search(self):
        """Search options and results should be localized."""

        service = ServiceFactory(status=Service.STATUS_CURRENT)
        self.load_page_and_set_language('fr')
        menu = self.wait_for_element('menu')
        search = menu.find_elements_by_link_text('Recherche')[0]
        search.click()
        form = self.wait_for_element('search_controls')
        self.assertHashLocation('/search')
        Select(form.find_element_by_name('type')).select_by_visible_text(
            service.type.name_fr)
        controls = self.wait_for_element('map-toggle', match=By.CLASS_NAME)
        controls.find_element_by_name('map-toggle-list').click()
        try:
            result = self.wait_for_element('.search-result-list > li', match=By.CSS_SELECTOR)
            name = result.find_element_by_class_name('name')
            name_text = name.text
        except StaleElementReferenceException:
            # Hit a race where we got a search element but then the page replaced it
            result = self.wait_for_element('.search-result-list > li', match=By.CSS_SELECTOR)
            name = result.find_element_by_class_name('name')
            name_text = name.text
        self.assertEqual(name_text, service.name_fr)
