from unittest.mock import patch
from django.contrib.gis.geos import Point

from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils import translation

from email_user.tests.factories import EmailUserFactory
from services.models import ServiceType, ProviderType, Provider, Service, \
    blank_or_at_least_one_letter, ServiceArea
from services.tests.factories import ProviderFactory, ServiceFactory, FeedbackFactory, \
    RequestForServiceFactory


class ProviderTest(TestCase):
    def test_related_name(self):
        # Just make sure we can get to the provider using user.provider
        user = EmailUserFactory()
        provider = ProviderFactory(
            user=user,
        )
        self.assertEqual(user.provider, provider)

    def test_str(self):
        # str returns name_en
        provider = Provider(name_en="Frederick")
        self.assertEqual("Frederick", str(provider))

    def test_num_beneficiaries_validation(self):
        data = [
            (None, True),  # No value is okay
            (-1, False),  # Range 0-1,000,000
            (0, True),
            (1000000, True),
            (1000001, False),
        ]
        for value, expect_valid in data:
            if expect_valid:
                ProviderFactory(number_of_monthly_beneficiaries=value).full_clean()
            else:
                with self.assertRaises(ValidationError):
                    ProviderFactory(number_of_monthly_beneficiaries=value).full_clean()

    def test_blank_or_at_least_one_letter(self):
        data = [
            ('', True),
            ('1', False),
            ('1111', False),
            ('11111a', True),
            (' ', False),
            ('&', False),
            ('2 Men & a Truck', True),
        ]
        for input, expected_result in data:
            self.assertEqual(expected_result, blank_or_at_least_one_letter(input))

    @override_settings(PHONE_NUMBER_REGEX=r'^\d{2}-\d{6}$')
    def test_phone_number_validation(self):
        with self.assertRaises(ValidationError):
            ProviderFactory(phone_number='9').full_clean()
        with self.assertRaises(ValidationError):
            ProviderFactory(phone_number='ab-cdefgh').full_clean()
        with self.assertRaises(ValidationError):
            ProviderFactory(phone_number='12-3456789').full_clean()
        with self.assertRaises(ValidationError):
            ProviderFactory(phone_number='12345678').full_clean()
        ProviderFactory(phone_number='12-345678').full_clean()


class ProviderTypeTest(TestCase):
    def test_str(self):
        # str() returns name in current language, or English
        obj = ProviderType(name_en="English", name_ar="Arabic", name_fr="French")
        translation.activate('fr')
        self.assertEqual("French", str(obj))
        translation.activate('ar')
        self.assertEqual("Arabic", str(obj))
        translation.activate('en')
        self.assertEqual("English", str(obj))
        translation.activate('de')
        self.assertEqual("English", str(obj))


class ServiceTypeTest(TestCase):
    def test_str(self):
        # str() returns name in current language
        obj = ServiceType(name_en="English", name_ar="Arabic", name_fr="French")
        translation.activate('fr')
        self.assertEqual("French", str(obj))
        translation.activate('ar')
        self.assertEqual("Arabic", str(obj))
        translation.activate('en')
        self.assertEqual("English", str(obj))
        translation.activate('de')
        self.assertEqual("English", str(obj))


class ServiceTest(TestCase):
    def test_str(self):
        # str returns name_en
        service = Service(name_en="Frederick")
        self.assertEqual("Frederick", str(service))

    def test_email_provider_about_approval(self):
        service = ServiceFactory()
        with patch('services.models.email_provider_about_service_approval_task') as mock_task:
            service.email_provider_about_approval()
        mock_task.delay.assert_called_with(service.pk)

    def test_cancel_cleans_up_pending_changes(self):
        service1 = ServiceFactory(status=Service.STATUS_CURRENT)
        # Make copy of service1 as an update
        service2 = Service.objects.get(pk=service1.pk)
        service2.pk = None
        service2.update_of = service1
        service2.status = Service.STATUS_DRAFT
        service2.save()
        service1.cancel()
        service2 = Service.objects.get(pk=service2.pk)
        self.assertEqual(Service.STATUS_CANCELED, service2.status)

    def test_approval_validation(self):
        service = ServiceFactory(location=None)
        # No location - should not allow approval
        try:
            service.validate_for_approval()
        except ValidationError as e:
            self.assertIn('location', e.error_dict)
        else:
            self.fail("Should have gotten ValidationError")
        # Add location, should be okay
        service.location = 'POINT(5 23)'
        service.validate_for_approval()
        # No name, should fail
        service.name_en = service.name_ar = service.name_fr = ''
        try:
            service.validate_for_approval()
        except ValidationError as e:
            self.assertIn('name', e.error_dict)
        else:
            self.fail("Should have gotten ValidationError")

    def test_get_longitude(self):
        service = ServiceFactory(location=None)
        self.assertIsNone(service.longitude)
        service = ServiceFactory(location='POINT( 1.0 2.0)')
        self.assertEqual(1.0, service.longitude)

    def test_set_longitude(self):
        service = ServiceFactory(location=None)
        service.longitude = -66.2
        self.assertEqual(Point(-66.2, 0), service.location)
        service = ServiceFactory(location='POINT( 1.0 2.0)')
        service.longitude = -66.2
        self.assertEqual(Point(-66.2, 2.0), service.location)

    def test_get_latitude(self):
        service = ServiceFactory(location=None)
        self.assertIsNone(service.latitude)
        service = ServiceFactory(location='POINT( 1.0 2.0)')
        self.assertEqual(2.0, service.latitude)

    def test_set_latitude(self):
        service = ServiceFactory(location=None)
        service.latitude = -66.2
        self.assertEqual(Point(0, -66.2), service.location)
        service = ServiceFactory(location='POINT( 1.0 2.0)')
        service.latitude = -66.2
        self.assertEqual(Point(1.0, -66.2), service.location)

    def test_mobile_services_have_location_set(self):
        # If a service is mobile, we set its location on save to the center of its area
        area = ServiceArea.objects.get(pk=1)  # Mount Lebanon/Baabda
        service = ServiceFactory(is_mobile=True, location=None, area_of_service=area)
        self.assertIsNotNone(service.location)
        self.assertEqual(area.centroid, service.location)

    def test_non_mobile_services_dont_have_location_set(self):
        # If a service is not mobile, we don't set its location on save
        area = ServiceArea.objects.get(pk=1)  # Mount Lebanon/Baabda
        service = ServiceFactory(location=None, area_of_service=area)
        self.assertIsNone(service.location)


class FeedbackTest(TestCase):
    def test_good_validation(self):
        # Factory ought to create a valid instance
        feedback = FeedbackFactory()
        feedback.full_clean()

    def test_delivered_but_some_required_fields_missing(self):
        feedback = FeedbackFactory(delivered=True, wait_time=None, wait_time_satisfaction=None)
        with self.assertRaises(ValidationError) as e:
            feedback.full_clean()
        self.assertIn('wait_time', e.exception.message_dict)
        self.assertIn('wait_time_satisfaction', e.exception.message_dict)

    def test_other_difficulties(self):
        feedback = FeedbackFactory(difficulty_contacting='other', other_difficulties='')
        with self.assertRaises(ValidationError) as e:
            feedback.full_clean()
        self.assertIn('other_difficulties', e.exception.message_dict)

    def test_non_delivery_explanation(self):
        feedback = FeedbackFactory(delivered=False, non_delivery_explained=None)
        with self.assertRaises(ValidationError) as e:
            feedback.full_clean()
        self.assertIn('non_delivery_explained', e.exception.message_dict)


class RequestForServiceTest(TestCase):
    def test_good_validation(self):
        # Factory ought to create a valid instance
        rfs = RequestForServiceFactory()
        rfs.full_clean()
