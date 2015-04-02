"""Integration tests for the single page front end."""

import shlex
import shutil
import subprocess
import tempfile
import time

from urllib.parse import urlparse

from django.conf import settings
from django.contrib.sites.models import Site
from django.test import LiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions

from email_user.tests.factories import EmailUserFactory
from services.tests.factories import ProviderTypeFactory


class FrontEndTestCase(LiveServerTestCase):
    """End to end testing with selenium and express server."""

    @classmethod
    def setUpClass(cls):
        cls.log_dir = tempfile.mkdtemp()
        cls.log_file, cls.log_file_name = tempfile.mkstemp(dir=cls.log_dir)
        cls.express_url = 'http://localhost:9000/'
        cls.express = subprocess.Popen(
            shlex.split('gulp startExpress --config test --port 9000 --fast'),
            cwd=settings.PROJECT_ROOT, stdout=cls.log_file, stderr=cls.log_file)
        cls.browser = webdriver.PhantomJS()
        # Set desktop size
        cls.browser.set_window_size(1280, 600)
        # Wait for server to be available
        time.sleep(1.5)
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        cls.express.terminate()
        super().tearDownClass()
        shutil.rmtree(cls.log_dir)

    def setUp(self):
        self.clear_storage()
        # # Django prior to 1.8 doesn't create the default site with the correct pk
        # # See https://code.djangoproject.com/ticket/23945
        defaults = {
            'domain':  'example.com',
            'name': 'example.com',
        }
        Site.objects.get_or_create(pk=settings.SITE_ID, defaults=defaults)

    def assertHashLocation(self, expected):
        """Assert current URL hash."""

        current = urlparse(self.browser.current_url)
        self.assertEqual(current.fragment, expected)

    def clear_storage(self):
        """Clear all browser local storage."""

        self.browser.get(self.express_url)
        self.browser.execute_script('localStorage.clear();')

    def set_language(self, language='en'):
        """Helper to set language choice in the browser."""

        self.browser.get(self.express_url)
        form = self.browser.find_element_by_id('language-toggle')
        button = form.find_element_by_css_selector('[data-lang="%s"]' % language)
        button.click()

    def wait_for_element(self, selector, match=By.ID, timeout=2):
        return WebDriverWait(self.browser, timeout).until(
            expected_conditions.visibility_of_element_located((match, selector))
        )

    def wait_for_page_title_contains(self, title, timeout=2):
        return WebDriverWait(self.browser, timeout).until(
            expected_conditions.text_to_be_present_in_element(
                (By.CLASS_NAME, 'page-title'), title)
        )

    def test_get_homepage(self):
        """Load the homepage."""

        self.browser.get(self.express_url)
        form = self.browser.find_element_by_id('language-toggle')
        self.assertTrue(form.is_displayed(), 'Language form should be visible.')

    def test_select_language(self):
        """Select user language."""

        self.set_language('fr')
        menu = self.wait_for_element('menu')
        language = menu.find_element_by_class_name('menu-item-language')
        self.assertEqual(language.text, 'Changer de langue', 'Menu should now be French')

    def test_login(self):
        """Login an existing user."""

        user = EmailUserFactory(password='abc123')
        self.set_language()
        menu = self.wait_for_element('menu')
        login = menu.find_elements_by_link_text('Login')[0]
        login.click()
        form = self.wait_for_element('form-login', match=By.CLASS_NAME)
        self.assertHashLocation('/login')
        data = {
            'email': user.email,
            'password': 'abc123',
        }
        for name, value in data.items():
            element = form.find_element_by_name(name)
            element.send_keys(value)
        form.find_element_by_class_name('submit').click()
        self.wait_for_element('services')
        self.assertHashLocation('/manage/service-list')

    def test_register(self):
        """Register for a new site account."""

        provider_type = ProviderTypeFactory()
        self.set_language()
        menu = self.wait_for_element('menu')
        registration = menu.find_elements_by_link_text('Provider Registration')[0]
        registration.click()
        form = self.wait_for_element('provider-form')
        self.assertHashLocation('/register')
        data = {
            'name': 'Joe Provider',
            'phone_number': '12-345678',
            'description': 'Test provider',
            'focal_point_name': 'John Doe',
            'focal_point_phone_number': '87-654321',
            'address': '1313 Mockingbird Lane, Beirut, Lebanon',
            'email': 'fred@example.com',
            'password1': 'foobar',
            'password2': 'foobar',
            'number_of_monthly_beneficiaries': '37',
        }
        for name, value in data.items():
            element = form.find_element_by_name(name)
            element.send_keys(value)
        # Select provider type
        select = Select(form.find_element_by_name('type'))
        select.select_by_visible_text(provider_type.name)
        form.find_element_by_class_name('form-btn-submit').click()
        self.wait_for_page_title_contains('Submitted Successfully', timeout=5)
        self.assertHashLocation('/register/confirm')
