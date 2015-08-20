from http.client import OK
import json

from django.core.urlresolvers import reverse
from django.test import TestCase

from services.models import Feedback, ProviderType, ServiceArea, ServiceType
from services.tests.factories import ServiceFactory, FeedbackFactory
from services.tests.test_api import APITestMixin


class ReportAPITest(APITestMixin, TestCase):

    def test_get_wait_times_non_staff(self):
        url = reverse('report-wait-times')
        rsp = self.get_with_token(url)
        self.assertEqual(OK, rsp.status_code)

    def test_get_wait_times(self):
        a_type = ServiceType.objects.first()
        service = ServiceFactory(type=a_type)
        FeedbackFactory(service=service, delivered=True, wait_time='lesshour')
        FeedbackFactory(service=service, delivered=True, wait_time='lesshour')
        FeedbackFactory(service=service, delivered=True, wait_time='more')
        url = reverse('report-wait-times')
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

    def test_get_qos_non_staff(self):
        url = reverse('report-qos')
        rsp = self.get_with_token(url)
        self.assertEqual(OK, rsp.status_code)

    def test_get_qos(self):
        a_type = ServiceType.objects.first()
        service = ServiceFactory(type=a_type)
        FeedbackFactory(service=service, delivered=True, quality=1)
        FeedbackFactory(service=service, delivered=True, quality=1)
        FeedbackFactory(service=service, delivered=True, quality=5)
        url = reverse('report-qos')
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

    def test_get_failure_non_staff(self):
        url = reverse('report-failure')
        rsp = self.get_with_token(url)
        self.assertEqual(OK, rsp.status_code)

    def test_get_failure(self):
        a_type = ServiceType.objects.first()
        service = ServiceFactory(type=a_type)
        FeedbackFactory(service=service, delivered=True, non_delivery_explained='no')
        FeedbackFactory(service=service, delivered=True, non_delivery_explained='no')
        FeedbackFactory(service=service, delivered=True, non_delivery_explained='yes')
        url = reverse('report-failure')
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

    def test_get_contact_non_staff(self):
        url = reverse('report-contact')
        rsp = self.get_with_token(url)
        self.assertEqual(OK, rsp.status_code)

    def test_get_contact(self):
        a_type = ServiceType.objects.first()
        service = ServiceFactory(type=a_type)
        FeedbackFactory(service=service, delivered=True, difficulty_contacting='no')
        FeedbackFactory(service=service, delivered=True, difficulty_contacting='no')
        FeedbackFactory(service=service, delivered=True, difficulty_contacting='other')
        url = reverse('report-contact')
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

    def test_get_communication_non_staff(self):
        url = reverse('report-communication')
        rsp = self.get_with_token(url)
        self.assertEqual(OK, rsp.status_code)

    def test_get_communication(self):
        a_type = ServiceType.objects.first()
        service = ServiceFactory(type=a_type)
        FeedbackFactory(service=service, delivered=True, staff_satisfaction=1)
        FeedbackFactory(service=service, delivered=True, staff_satisfaction=1)
        FeedbackFactory(service=service, delivered=True, staff_satisfaction=5)
        url = reverse('report-communication')
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

    def test_get_num_by_service_type_non_staff(self):
        url = reverse('report-num-services-by-service-type')
        rsp = self.get_with_token(url)
        self.assertEqual(OK, rsp.status_code)

    def test_get_num_by_service_type(self):
        a_type = ServiceType.objects.first()
        b_type = ServiceType.objects.last()
        a_service_area = ServiceArea.objects.first()
        b_service_area = ServiceArea.objects.first()
        # 1 service:  area a, type a
        ServiceFactory(area_of_service=a_service_area, type=a_type)
        # 2 services: area b, type b
        ServiceFactory(area_of_service=b_service_area, type=b_type)
        ServiceFactory(area_of_service=b_service_area, type=b_type)

        url = reverse('report-num-services-by-service-type')
        rsp = self.get_with_token(url)
        self.assertEqual(OK, rsp.status_code)
        result = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual(len(result), ServiceType.objects.all().count())
        for r in result:
            if r['number'] == a_type.number:
                for t in r['totals']:
                    if t['label_en'] == a_service_area.name_en:
                        self.assertEqual(1, t['total'])
                    else:
                        self.assertEqual(0, t['total'])
            elif r['number'] == b_type.number:
                for t in r['totals']:
                    if t['label_en'] == b_service_area.name_en:
                        self.assertEqual(2, t['total'])
                    else:
                        self.assertEqual(0, t['total'])
            else:
                self.assertTrue(all([t['total'] == 0 for t in r['totals']]))

    def test_get_num_by_provider_type_non_staff(self):
        url = reverse('report-num-services-by-provider-type')
        rsp = self.get_with_token(url)
        self.assertEqual(OK, rsp.status_code)

    def test_get_num_by_provider_type(self):
        a_type = ProviderType.objects.first()
        b_type = ProviderType.objects.last()
        a_service_area = ServiceArea.objects.first()
        b_service_area = ServiceArea.objects.first()
        # 1 service:  area a, type a
        ServiceFactory(area_of_service=a_service_area, provider__type=a_type)
        # 2 services: area b, type b
        ServiceFactory(area_of_service=b_service_area, provider__type=b_type)
        ServiceFactory(area_of_service=b_service_area, provider__type=b_type)

        url = reverse('report-num-services-by-provider-type')
        rsp = self.get_with_token(url)
        self.assertEqual(OK, rsp.status_code)
        result = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual(len(result), ProviderType.objects.all().count())
        for r in result:
            if r['number'] == a_type.number:
                for t in r['totals']:
                    if t['label_en'] == a_service_area.name_en:
                        self.assertEqual(1, t['total'])
                    else:
                        self.assertEqual(0, t['total'])
            elif r['number'] == b_type.number:
                for t in r['totals']:
                    if t['label_en'] == b_service_area.name_en:
                        self.assertEqual(2, t['total'])
                    else:
                        self.assertEqual(0, t['total'])
            else:
                self.assertTrue(all([t['total'] == 0 for t in r['totals']]))
