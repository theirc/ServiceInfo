from http.client import CREATED, OK, NOT_FOUND

from django.core.urlresolvers import reverse
from django.forms import model_to_dict
from django.test import TestCase

from services.models import ServiceArea, Nationality, Service
from services.tests.factories import FeedbackFactory


class FeedbackTest(TestCase):
    # The feedback API is write-only
    def try_to_create_one_like(self, example):
        example.full_clean()  # double-check it's valid
        data = model_to_dict(example)
        del data['id']
        data['area_of_residence'] = \
            ServiceArea.objects.get(pk=data['area_of_residence']).get_api_url()
        data['nationality'] = Nationality.objects.get(pk=data['nationality']).get_api_url()
        data['service'] = Service.objects.get(pk=data['service']).get_api_url()
        # Remove any fields whose value is None
        data = {k: v for k, v in data.items() if v is not None}
        rsp = self.client.post(reverse('feedback-list'), data=data)
        self.assertEqual(CREATED, rsp.status_code, msg=rsp.content.decode('utf-8'))

    def test_create_delivered_feedback(self):
        example = FeedbackFactory(delivered=True)
        self.try_to_create_one_like(example)

    def test_create_undelivered_feedback(self):
        example = FeedbackFactory(delivered=False)
        self.try_to_create_one_like(example)

    def test_cannot_get_feedback(self):
        # Feedback is write-only
        feedback = FeedbackFactory()
        # `reverse` doesn't even work because there's no such URL defined anywhere
        # url = reverse('feedback-detail', args=[self.id])
        url = '/api/feedbacks/%d/' % feedback.pk
        rsp = self.client.get(url)
        self.assertEqual(NOT_FOUND, rsp.status_code, msg=rsp.content.decode('utf-8'))


class NationalityTest(TestCase):
    def test_nationalities(self):
        # Get list of nationalities
        url = reverse('nationality-list')
        print(url)
        rsp = self.client.get(url)
        self.assertEqual(OK, rsp.status_code, msg=rsp.content.decode('utf-8'))
