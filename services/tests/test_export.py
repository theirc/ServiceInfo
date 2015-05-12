from datetime import time
from http.client import OK, FORBIDDEN
from io import BytesIO
import json
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from xlrd import open_workbook
from xlwt import Workbook as xlwt_Workbook
from email_user.tests.factories import EmailUserFactory
from services.import_export import get_export_workbook, PROVIDER_HEADINGS, SERVICE_HEADINGS, \
    SELECTION_CRITERIA_HEADINGS, SERVICES_SHEET_NAME, SELECTION_CRITERIA_SHEET_NAME, \
    PROVIDER_SHEET_NAME, get_export_workbook_for_user, validate_and_import_data
from services.models import Provider, Service, SelectionCriterion
from services.tests.factories import ProviderFactory, ServiceFactory, SelectionCriterionFactory


def get_book_bits(workbook):
    assert isinstance(workbook, xlwt_Workbook)
    bytes = BytesIO()
    workbook.save(bytes)
    return bytes.getvalue()


def save_and_read_book(workbook):
    """
    Given an xlwt workbook object, save it to bits, then read those
    bits using xlrd to get a new xlrd workbook object.
    Makes sure what we have is a valid Excel sheet - or as close as
    we can come without actually loading it in Excel.
    """
    bytes = get_book_bits(workbook)
    return open_workbook(file_contents=bytes, on_demand=True)


class ExportURLTest(TestCase):
    def setUp(self):
        self.email = 'joe@example.com'
        self.password = 'password'
        self.user = get_user_model().objects.create_user(
            password=self.password,
            email=self.email,
        )
        self.token = Token.objects.get(user=self.user).key
        self.api_client = APIClient()
        self.token = Token.objects.get(user=self.user).key

    def get_with_token(self, url):
        """
        Make a GET to a url, passing self.token in the request headers.
        Return the response.
        """
        return self.api_client.get(
            url,
            HTTP_SERVICEINFOAUTHORIZATION="Token %s" % self.token
        )

    def get_export_url(self):
        # using the API
        rsp = self.get_with_token('/api/export/')
        self.assertEqual(OK, rsp.status_code, msg=rsp.content.decode('utf-8'))
        return json.loads(rsp.content.decode('utf-8'))['url']

    def test_using_export_url_to_get_export(self):
        provider = ProviderFactory(user=self.user)
        ServiceFactory(provider=provider, status=Service.STATUS_CURRENT)
        url = self.get_export_url()
        rsp = self.client.get(url)
        self.assertEqual(OK, rsp.status_code)
        bits = rsp.content
        errs = validate_and_import_data(self.user, bits)
        self.assertFalse(errs)

    @override_settings(SIGNED_URL_LIFETIME=-1)
    def test_expired_export_url(self):
        url = self.get_export_url()
        rsp = self.client.get(url)
        self.assertEqual(FORBIDDEN, rsp.status_code)


class ExportUtilsTest(TestCase):

    def test_empty_export(self):
        book = save_and_read_book(get_export_workbook([]))

        self.assertEqual(3, book.nsheets)

        sheet = book.get_sheet(0)
        self.assertEqual(PROVIDER_SHEET_NAME, sheet.name)
        self.assertEqual(1, sheet.nrows)
        self.assertEqual(len(PROVIDER_HEADINGS), sheet.ncols)

        sheet = book.get_sheet(1)
        self.assertEqual(SERVICES_SHEET_NAME, sheet.name)
        self.assertEqual(1, sheet.nrows)
        self.assertEqual(len(SERVICE_HEADINGS), sheet.ncols)

        sheet = book.get_sheet(2)
        self.assertEqual(SELECTION_CRITERIA_SHEET_NAME, sheet.name)
        self.assertEqual(1, sheet.nrows)
        self.assertEqual(len(SELECTION_CRITERIA_HEADINGS), sheet.ncols)

    def test_random_data(self):
        provider = ProviderFactory()
        service1 = ServiceFactory(provider=provider, status=Service.STATUS_CURRENT)
        service2 = ServiceFactory(provider=provider, status=Service.STATUS_CURRENT)
        ServiceFactory(provider=provider, status=Service.STATUS_CURRENT)
        # Some additional services that should not show up
        ServiceFactory(status=Service.STATUS_CURRENT)  # not one of the providers we want
        ServiceFactory(provider=provider, status=Service.STATUS_DRAFT)  # Draft mode
        SelectionCriterionFactory(service=service1)
        SelectionCriterionFactory(service=service2)
        SelectionCriterionFactory()  # unwanted service

        # Querysets of just the objects we expect to be exported
        providers = Provider.objects.order_by('id')
        services = Service.objects.filter(status=Service.STATUS_CURRENT,
                                          provider__in=providers).order_by('id')
        criteria = SelectionCriterion.objects.filter(service__status=Service.STATUS_CURRENT,
                                                     service__provider__in=providers).order_by('id')

        xlwt_book = get_export_workbook(providers)
        book = save_and_read_book(xlwt_book)

        # First sheet - providers
        sheet = book.get_sheet(0)
        self.assertEqual(providers.count(), sheet.nrows - 1)
        self.assertEqual(PROVIDER_HEADINGS, sheet.row_values(0))
        for i, rownum in enumerate(range(1, sheet.nrows)):
            values = sheet.row_values(rownum)
            provider = providers[i]
            data = dict(zip(PROVIDER_HEADINGS, values))
            self.assertEqual(provider.id, data['id'])
            self.assertEqual(provider.name_ar, data['name_ar'])

        # Second sheet = services
        sheet = book.get_sheet(1)
        self.assertEqual(services.count(), sheet.nrows - 1)
        self.assertEqual(SERVICE_HEADINGS, sheet.row_values(0))
        for i, rownum in enumerate(range(1, sheet.nrows)):
            values = sheet.row_values(rownum)
            service = services[i]
            data = dict(zip(SERVICE_HEADINGS, values))
            self.assertEqual(service.id, data['id'])
            self.assertEqual(service.name_ar, data['name_ar'])
            provider = Provider.objects.get(id=data['provider__id'])
            self.assertEqual(provider, service.provider)

        # Third sheet - selection criteria
        sheet = book.get_sheet(2)
        self.assertEqual(SELECTION_CRITERIA_HEADINGS, sheet.row_values(0))
        self.assertEqual(criteria.count(), sheet.nrows - 1)
        for i, rownum in enumerate(range(1, sheet.nrows)):
            values = sheet.row_values(rownum)
            criterion = criteria[i]
            data = dict(zip(SELECTION_CRITERIA_HEADINGS, values))
            self.assertEqual(criterion.id, data['id'])
            self.assertEqual(criterion.text_ar, data['text_ar'])
            service = Service.objects.get(id=data['service__id'])
            self.assertEqual(service, criterion.service)

        # The exported workbook should also be valid for import by
        # a staff user
        user = EmailUserFactory(is_staff=True)
        validate_and_import_data(user, get_book_bits(xlwt_book))

    def test_non_staff_sees_all_current_data(self):
        provider = ProviderFactory()
        service1 = ServiceFactory(provider=provider, status=Service.STATUS_CURRENT)
        service2 = ServiceFactory(provider=provider, status=Service.STATUS_CURRENT)
        ServiceFactory(status=Service.STATUS_CURRENT)
        ServiceFactory(provider=provider, status=Service.STATUS_DRAFT)  # Draft - not included
        book = get_export_workbook_for_user(provider.user)
        xlrd_book = save_and_read_book(book)

        # First sheet - providers
        sheet = xlrd_book.get_sheet(0)
        self.assertEqual(2, sheet.nrows - 1)
        # first provider
        values = sheet.row_values(1)
        data = dict(zip(PROVIDER_HEADINGS, values))
        self.assertEqual(provider.id, data['id'])

        # Second sheet - services
        sheet = xlrd_book.get_sheet(1)
        self.assertEqual(3, sheet.nrows - 1)
        values = sheet.row_values(1)
        data = dict(zip(SERVICE_HEADINGS, values))
        self.assertEqual(service1.id, data['id'])
        values = sheet.row_values(2)
        data = dict(zip(SERVICE_HEADINGS, values))
        self.assertEqual(service2.id, data['id'])

    def test_staff_see_all_current_data(self):
        user = EmailUserFactory(is_staff=True)
        provider = ProviderFactory()
        ProviderFactory()
        ServiceFactory(provider=provider, status=Service.STATUS_CURRENT)
        ServiceFactory(provider=provider, status=Service.STATUS_CURRENT)
        ServiceFactory(status=Service.STATUS_CURRENT)
        ServiceFactory(provider=provider, status=Service.STATUS_DRAFT)
        book = get_export_workbook_for_user(user)
        xlrd_book = save_and_read_book(book)

        # First sheet - providers
        sheet = xlrd_book.get_sheet(0)
        self.assertEqual(3, sheet.nrows - 1)

        # Second sheet - services
        sheet = xlrd_book.get_sheet(1)
        self.assertEqual(3, sheet.nrows - 1)

    def test_location_exported_as_lat_long(self):
        provider = ProviderFactory()
        service1 = ServiceFactory(provider=provider, status=Service.STATUS_CURRENT)
        book = get_export_workbook_for_user(provider.user)
        xlrd_book = save_and_read_book(book)
        sheet = xlrd_book.get_sheet(1)
        values = sheet.row_values(1)
        data = dict(zip(SERVICE_HEADINGS, values))
        self.assertEqual(service1.longitude, data['longitude'])
        self.assertEqual(service1.latitude, data['latitude'])

    def test_open_close_as_hh_mm(self):
        provider = ProviderFactory()
        ServiceFactory(provider=provider, status=Service.STATUS_CURRENT,
                       wednesday_close=time(18, 23)
                       )
        book = get_export_workbook_for_user(provider.user)
        xlrd_book = save_and_read_book(book)
        sheet = xlrd_book.get_sheet(1)
        values = sheet.row_values(1)
        data = dict(zip(SERVICE_HEADINGS, values))
        self.assertEqual('', data['sunday_open'])
        self.assertEqual('18:23', data['wednesday_close'])
