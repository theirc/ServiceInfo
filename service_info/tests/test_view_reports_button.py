import time

from email_user.tests.factories import EmailUserFactory
from service_info.tests.test_frontend import ServiceInfoFrontendTestCase


class ViewReportsButtonTest(ServiceInfoFrontendTestCase):

    def test_logout_and_login_as_staff(self):
        # Staff user sees the reports button even after logging out and in
        self.password = 'abc123'
        self.user = EmailUserFactory(password=self.password)
        self.user.is_staff = True
        self.user.save()
        self.load_page_and_set_language()
        self.login()
        button = self.wait_for_element('view_reports_button')
        self.assertTrue(button.is_displayed())
        self.logout()
        # Give the page time to start reloading before looking for the button again
        time.sleep(1)
        self.login()
        # Give the page time to start reloading before looking for the button again
        time.sleep(1)
        button = self.wait_for_element('view_reports_button')
        self.assertTrue(button.is_displayed())
        # User can view reports page
        button.click()
        self.wait_for_element('report-table')

    def test_logout_and_login_as_non_staff(self):
        # Non-staff user sees the reports button, even after logging out
        # and in and changing language.  Even if superuser.
        self.password = 'abc123'
        self.user = EmailUserFactory(password=self.password)
        self.user.is_superuser = True
        self.user.save()
        self.load_page_and_set_language()
        self.login()
        button = self.wait_for_element('view_reports_button', must_be_visible=False)
        self.assertTrue(button.is_displayed())

        # Log out and in again
        self.logout()
        # Give the page time to start reloading before looking for the menu again
        time.sleep(0.5)
        self.login()
        # Give the page time to start reloading before looking for the button again
        time.sleep(0.5)
        button = self.wait_for_element('view_reports_button', must_be_visible=False)
        self.assertTrue(button.is_displayed())

        # Set the language again
        form = self.wait_for_element('language-toggle')
        button = form.find_element_by_css_selector('[data-lang="%s"]' % 'en')
        button.click()
        # Give the page time to start reloading before looking for the button again
        time.sleep(0.5)
        button = self.wait_for_element('view_reports_button', must_be_visible=False)
        self.assertTrue(button.is_displayed())

        # User can view reports page
        button.click()
        self.wait_for_element('report-table')
