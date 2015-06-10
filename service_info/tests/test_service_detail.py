import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from service_info.tests.test_frontend import ServiceInfoFrontendTestCase, DEFAULT_TIMEOUT
from services.models import Service
from services.tests.factories import ServiceFactory


class ServiceDetailTest(ServiceInfoFrontendTestCase):

    def test_service_detail_page(self):
        service = ServiceFactory(status=Service.STATUS_CURRENT)
        self.load_page_and_set_language()
        menu = self.wait_for_element('menu')
        search = menu.find_elements_by_link_text('Search')[0]
        search.click()
        form = self.wait_for_element('search_controls')
        self.assertHashLocation('/search')
        form.find_element_by_name('filtered-search').send_keys(
            service.provider.name_en[:5])
        # Results are updated automatically as search characters are entered
        # Wait a sec to make sure we have the final results
        time.sleep(1)
        result = self.wait_for_element('.search-result-list > li', match=By.CSS_SELECTOR)
        name = result.find_element_by_class_name('name')
        self.assertEqual(name.text, service.name_en)

        # Click the service's name to go to its detail page
        link = name.find_element(by=By.TAG_NAME, value='a')
        link.click()

        # Its cost should be displayed in the cost-of-service element
        WebDriverWait(self.browser, DEFAULT_TIMEOUT).until(
            expected_conditions.text_to_be_present_in_element(
                (By.ID, 'cost-of-service'), service.cost_of_service)
        )
