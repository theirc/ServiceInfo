"""Integration tests for the single page front end."""

import shlex
import shutil
import subprocess
import tempfile
import time

from django.conf import settings
from django.test import LiveServerTestCase

from selenium import webdriver


class FrontEndTestCase(LiveServerTestCase):
    """Base test class to setup selenium and express server for end to end testing."""

    @classmethod
    def setUpClass(cls):
        cls.log_dir = tempfile.mkdtemp()
        cls.log_file, cls.log_file_name = tempfile.mkstemp(dir=cls.log_dir)
        cls.express_url = 'http://localhost:9000/'
        cls.express = subprocess.Popen(
            shlex.split('gulp startExpress --config test --port 9000 --fast'),
            cwd=settings.PROJECT_ROOT, stdout=cls.log_file, stderr=cls.log_file)
        cls.browser = webdriver.PhantomJS()
        # Wait for server to be available
        time.sleep(1.5)
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        cls.express.terminate()
        super().tearDownClass()
        shutil.rmtree(cls.log_dir)

    def test_get_homepage(self):
        """Load the homepage."""

        self.browser.get(self.express_url)
        form = self.browser.find_element_by_id('language-toggle')
        self.assertTrue(form.is_displayed(), 'Language form should be visible.')
