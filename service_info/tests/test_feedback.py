import time
from selenium.common.exceptions import TimeoutException, WebDriverException

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from service_info.tests.test_frontend import ServiceInfoFrontendTestCase, DEFAULT_TIMEOUT
from services.models import Service, Nationality, ServiceArea, Feedback
from services.tests.factories import ServiceFactory


class FeedbackTest(ServiceInfoFrontendTestCase):

    def test_feedback_page_delivered(self):
        self.assertFalse(Feedback.objects.all().exists())

        service = ServiceFactory(status=Service.STATUS_CURRENT)
        self.load_page_and_set_language()
        menu = self.wait_for_element('menu')
        feedback = menu.find_elements_by_link_text('Give Feedback')[0]
        feedback.click()
        form = self.wait_for_element('search_controls')
        self.assertHashLocation('/feedback/list')
        service_name = self.wait_for_element(
            'a[href="#/service/%d"]' % service.id, match=By.CSS_SELECTOR)
        service_name.click()

        feedback_button = self.wait_for_element(
            'a[href="#/feedback/%d"] button' % service.id,
            match=By.CSS_SELECTOR)
        feedback_button.click()

        self.wait_for_element('input[name=anonymous]', match=By.CSS_SELECTOR)

        # Fill in the form
        form = self.wait_for_element('form', match=By.CSS_SELECTOR)

        def click_element(selector):
            form.find_element(value=selector, by=By.CSS_SELECTOR).click()

        def type_in_element(selector, text):
            try:
                self.wait_for_element(selector, match=By.CSS_SELECTOR, must_be_visible=True).send_keys(text)
            except TimeoutException:
                print("Timeout waiting for %s to appear, continuing anyway" % selector)

        type_in_element('[name=name]', 'John Doe')
        type_in_element('[name=phone_number]', '12-345678')
        iraqi_nationality = Nationality.objects.get(name_en='Iraqi')
        click_element('select[name=nationality] option[value$="/%d/"]' % iraqi_nationality.id)

        area = ServiceArea.objects.first()
        click_element('select[name=area_of_residence] option[value$="/%d/"]' % area.id)
        click_element('input[name=anonymous][value="1"]')
        click_element('input[name=delivered][value="1"]')

        # Wait for javascript to display the "delivered" fields
        self.wait_for_element('input[name=quality][value="4"]', match=By.CSS_SELECTOR, must_be_visible=True)

        click_element('input[name=quality][value="4"]')
        click_element('input[name=staff_satisfaction][value="2"]')
        click_element('select[name=wait_time] option[value="3-7days"]')
        click_element('input[name=wait_time_satisfaction][value="1"]')
        click_element('select[name=difficulty_contacting] option[value=other]')
        # Wait for JS again
        self.wait_for_element('textarea[name=other_difficulties]', match=By.CSS_SELECTOR, must_be_visible=True)
        type_in_element('textarea[name=other_difficulties]', 'Other difficulties')

        type_in_element('textarea[name=extra_comments]', 'Other comments')

        self.browser.get_screenshot_as_file("pre_submit.png")

        # Submit
        submit_button = self.wait_for_element('button.form-btn-submit', match=By.CSS_SELECTOR).click()

        # Wait
        try:
            self.wait_for_element('a[href="#/feedback/list"]', match=By.CSS_SELECTOR)
        except WebDriverException as e:
            self.browser.get_screenshot_as_file("screenshot.png")
            print("ERROR waiting for feedback confirmation page, ignoring for now.")
            print("Screenshot in screenshot.png")
            print(e)

        self.browser.get_screenshot_as_file("post_submit.png")

        # Did we get a Feedback object?
        if not Feedback.objects.exists():
            self.fail("SOME error occurred, see screenshots pre_submit.png and post_submit.png")

        # Find the submitted form
        self.assertEqual(1, Feedback.objects.all().count())
        feedback = Feedback.objects.first()
        self.assertEqual('John Doe', feedback.name)
        self.assertEqual('12-345678', feedback.phone_number)
        self.assertEqual(iraqi_nationality, feedback.nationality)
        self.assertEqual(area, feedback.area_of_residence)
        self.assertEqual(service, feedback.service)
        self.assertEqual(True, feedback.delivered)
        self.assertEqual(4, feedback.quality)
        self.assertFalse(feedback.non_delivery_explained)
        self.assertEqual('3-7days', feedback.wait_time)
        self.assertEqual(1, feedback.wait_time_satisfaction)
        self.assertEqual('other', feedback.difficulty_contacting)
        self.assertEqual('Other difficulties', feedback.other_difficulties)
        self.assertEqual(2, feedback.staff_satisfaction)
        self.assertEqual('Other comments', feedback.extra_comments)
        self.assertEqual(True, feedback.anonymous)
