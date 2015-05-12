from http.client import OK
import json
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse
from django.test import TestCase
from services.models import ServiceType, Feedback
from services.tests.factories import ServiceFactory, FeedbackFactory
from services.tests.test_api import APITestMixin


class ServiceTypeAPITest(APITestMixin, TestCase):
    def test_get_types(self):
        rsp = self.get_with_token(reverse('servicetype-list'))
        self.assertEqual(OK, rsp.status_code)
        results = json.loads(rsp.content.decode('utf-8'))
        result = results[0]
        self.assertIn('icon_url', result)
        icon_url = result['icon_url']
        self.assertTrue(icon_url.startswith(settings.MEDIA_URL))
        path = icon_url.replace(settings.MEDIA_URL, '')
        self.assertTrue(default_storage.exists(path))

    def test_get_type(self):
        # Try it unauthenticated
        a_type = ServiceType.objects.first()
        url = a_type.get_api_url()
        rsp = self.client.get(url)
        self.assertEqual(OK, rsp.status_code)
        result = json.loads(rsp.content.decode('utf-8'))
        self.assertIn('icon_url', result)
        icon_url = result['icon_url']
        self.assertTrue(icon_url.startswith(settings.MEDIA_URL))
        path = icon_url.replace(settings.MEDIA_URL, '')
        self.assertTrue(default_storage.exists(path))

    def test_get_wait_times(self):
        a_type = ServiceType.objects.first()
        service = ServiceFactory(type=a_type)
        FeedbackFactory(service=service, delivered=True, wait_time='lesshour')
        FeedbackFactory(service=service, delivered=True, wait_time='lesshour')
        FeedbackFactory(service=service, delivered=True, wait_time='more')
        url = reverse('servicetype-wait-times')
        rsp = self.get_with_token(url)
        self.assertEqual(OK, rsp.status_code)
        result = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual(len(result), ServiceType.objects.all().count())
        for r in result:
            if r['number'] == a_type.number:
                # less than hour, 1-2 days, 3-7 days, 1-2 weeks, more than 2 weeks
                expected_totals = [2, 0, 0, 0, 1, ]
            else:
                expected_totals = [0, 0, 0, 0, 0, ]
            expected_labels = [
                'Less than 1 hour', 'Up to 2 days', '3-7 days',
                '1-2 weeks', 'More than 2 weeks']
            self.assertIn('totals', r)
            totals = r['totals']
            self.assertEqual([t['label_en'] for t in totals], expected_labels)
            self.assertEqual([t['total'] for t in totals], expected_totals)

    def test_get_qos(self):
        a_type = ServiceType.objects.first()
        service = ServiceFactory(type=a_type)
        FeedbackFactory(service=service, delivered=True, quality=1)
        FeedbackFactory(service=service, delivered=True, quality=1)
        FeedbackFactory(service=service, delivered=True, quality=5)
        url = reverse('servicetype-qos')
        rsp = self.get_with_token(url)
        self.assertEqual(OK, rsp.status_code)
        result = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual(len(result), ServiceType.objects.all().count())
        for r in result:
            if r['number'] == a_type.number:
                # 1, 2, 3, 4, 5
                expected_totals = [2, 0, 0, 0, 1, ]
            else:
                expected_totals = [0, 0, 0, 0, 0, ]
            expected_labels = ['1', '2', '3', '4', '5']
            self.assertIn('totals', r)
            totals = r['totals']
            self.assertEqual([t['label_en'] for t in totals], expected_labels)
            self.assertEqual([t['total'] for t in totals], expected_totals)

    def test_get_failure(self):
        a_type = ServiceType.objects.first()
        service = ServiceFactory(type=a_type)
        FeedbackFactory(service=service, delivered=True, non_delivery_explained='no')
        FeedbackFactory(service=service, delivered=True, non_delivery_explained='no')
        FeedbackFactory(service=service, delivered=True, non_delivery_explained='yes')
        url = reverse('servicetype-failure')
        rsp = self.get_with_token(url)
        self.assertEqual(OK, rsp.status_code)
        result = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual(len(result), ServiceType.objects.all().count())
        for r in result:
            if r['number'] == a_type.number:
                # 1, 2, 3, 4, 5
                expected_totals = [2, 0, 0, 1, ]
            else:
                expected_totals = [0, 0, 0, 0, ]
            field = Feedback._meta.get_field('non_delivery_explained')

            expected_labels = [str(label) for value, label in field.choices]
            self.assertIn('totals', r)
            totals = r['totals']
            self.assertEqual([t['label_en'] for t in totals], expected_labels)
            self.assertEqual([t['total'] for t in totals], expected_totals)

    def test_get_context(self):
        a_type = ServiceType.objects.first()
        service = ServiceFactory(type=a_type)
        FeedbackFactory(service=service, delivered=True, difficulty_contacting='no')
        FeedbackFactory(service=service, delivered=True, difficulty_contacting='no')
        FeedbackFactory(service=service, delivered=True, difficulty_contacting='other')
        url = reverse('servicetype-contact')
        rsp = self.get_with_token(url)
        self.assertEqual(OK, rsp.status_code)
        result = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual(len(result), ServiceType.objects.all().count())
        for r in result:
            if r['number'] == a_type.number:
                # 1, 2, 3, 4, 5
                expected_totals = [2, 0, 0, 0, 0, 1, ]
            else:
                expected_totals = [0, 0, 0, 0, 0, 0]
            field = Feedback._meta.get_field('difficulty_contacting')

            expected_labels = [str(label) for value, label in field.choices]
            self.assertIn('totals', r)
            totals = r['totals']
            self.assertEqual([t['label_en'] for t in totals], expected_labels)
            self.assertEqual([t['total'] for t in totals], expected_totals)

    def test_get_communication(self):
        a_type = ServiceType.objects.first()
        service = ServiceFactory(type=a_type)
        FeedbackFactory(service=service, delivered=True, staff_satisfaction=1)
        FeedbackFactory(service=service, delivered=True, staff_satisfaction=1)
        FeedbackFactory(service=service, delivered=True, staff_satisfaction=5)
        url = reverse('servicetype-communication')
        rsp = self.get_with_token(url)
        self.assertEqual(OK, rsp.status_code)
        result = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual(len(result), ServiceType.objects.all().count())
        for r in result:
            if r['number'] == a_type.number:
                # 1, 2, 3, 4, 5
                expected_totals = [2, 0, 0, 0, 1, ]
            else:
                expected_totals = [0, 0, 0, 0, 0]

            expected_labels = ['1', '2', '3', '4', '5']
            self.assertIn('totals', r)
            totals = r['totals']
            self.assertEqual([t['label_en'] for t in totals], expected_labels)
            self.assertEqual([t['total'] for t in totals], expected_totals)
