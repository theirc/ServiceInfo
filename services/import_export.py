from collections import defaultdict
from datetime import time
import logging

from django.db import transaction
from django.utils.translation import ugettext as _

from xlrd import open_workbook, XLRDError
import xlwt

from services.forms import ProviderForm, ServiceForm, SelectionCriterionForm
from services.models import Service, SelectionCriterion, Provider


logger = logging.getLogger(__name__)


PROVIDER_SHEET_NAME = "Providers"
PROVIDER_HEADINGS = [
    'id',
    'name_en',
    'name_ar',
    'name_fr',
    'type__number',
    'type__name_en',
    'type__name_ar',
    'type__name_fr',
    'phone_number',
    'website',
    'description_en',
    'description_ar',
    'description_fr',
    'focal_point_name_en',
    'focal_point_name_ar',
    'focal_point_name_fr',
    'focal_point_phone_number',
    'address_en',
    'address_ar',
    'address_fr',
    'email',
    'number_of_monthly_beneficiaries',
    'password'
]


SERVICES_SHEET_NAME = 'Services'
SERVICE_HEADINGS = [
    'id',
    'provider__id',
    'name_en',
    'name_ar',
    'name_fr',
    'area_of_service__name_en',
    'area_of_service__name_ar',
    'area_of_service__name_fr',
    'description_en',
    'description_ar',
    'description_fr',
    'additional_info_en',
    'additional_info_ar',
    'additional_info_fr',
    'cost_of_service',
    'update_of__id',
    'longitude',
    'latitude',
    'sunday_open', 'sunday_close',
    'monday_open', 'monday_close',
    'tuesday_open', 'tuesday_close',
    'wednesday_open', 'wednesday_close',
    'thursday_open', 'thursday_close',
    'friday_open', 'friday_close',
    'saturday_open', 'saturday_close',
    'type__number',
    'type__name_en',
    'type__name_ar',
    'type__name_fr',
]

SELECTION_CRITERIA_SHEET_NAME = 'Selection Criteria'
SELECTION_CRITERIA_HEADINGS = [
    'id',
    'service__id',
    'text_en',
    'text_ar',
    'text_fr',
]


def valid_providers_for_user(user):
    """Return queryset of providers that this user is authorized
    to export/import"""
    if user.is_staff:
        providers = Provider.objects.all()
    else:
        providers = Provider.objects.filter(user=user)
    return providers


def get_export_workbook(providers, services=None, criteria=None, cell_overwrite_ok=False):
    """
    Given a queryset of providers, return an xlwt Workbook with the exported
    data for those providers.

    :param providers:
    :param services: If None, export all the services of the specified providers. Otherwise,
    services should be an iterable of Service objects that will be exported without regard
    to whether they belong to the exported providers.
    :param criteria: If None, export all the criteria of the specified services. Otherwise,
    criteria should be an iterable of SelectionCriterion objects that will be exported
    without regard to whether they belong to the exported services.
    :param cell_overwrite_ok: Should not be set except in tests, since it's only in tests
    that we should ever overwrite a cell.
    :return: xlwt.Workbook
    """
    book = xlwt.Workbook(encoding='utf-8')

    # Providers
    provider_sheet = book.add_sheet(PROVIDER_SHEET_NAME, cell_overwrite_ok=cell_overwrite_ok)
    add_models_to_sheet(provider_sheet, PROVIDER_HEADINGS, providers)

    # Services
    if services is None:
        services = Service.objects.filter(status=Service.STATUS_CURRENT,
                                          provider__in=providers).order_by('provider__id', 'id')
    service_sheet = book.add_sheet(SERVICES_SHEET_NAME, cell_overwrite_ok=cell_overwrite_ok)
    add_models_to_sheet(service_sheet, SERVICE_HEADINGS, services)

    # Selection criteria
    criteria_sheet = book.add_sheet(SELECTION_CRITERIA_SHEET_NAME,
                                    cell_overwrite_ok=cell_overwrite_ok)
    if criteria is None:
        criteria = SelectionCriterion.objects.filter(service__in=services)\
            .order_by('service__id', 'id')
    add_models_to_sheet(criteria_sheet, SELECTION_CRITERIA_HEADINGS, criteria)

    return book


def get_export_workbook_for_user(user):
    """
    Given a user, return an xlwt Workbook object with the exported
    data that the user is entitled to see.
    :param user:
    :return: xlwt.Workbook
    """
    return get_export_workbook(valid_providers_for_user(user))


def add_models_to_sheet(sheet, headings, records):
    """
    Given an xlwt Worksheet, an iterable of heading strings, and a queryset
    of model objects, add the headings and model data to the sheet starting
    with row 0.

    (This is not really a generic function; it has some custom handling
    for our own models.)

    :param sheet: xlwt Worksheet
    :param headings: iterable of heading strings
    :param records: queryset of model instances
    """
    write_row(sheet, 0, headings)
    row = 1
    for record in records:
        data = []
        for head in headings:
            # HACKS: These are specially coded for our models.
            if head == 'email':
                data.append(record.user.email)
            elif head == 'location':
                data.append(str(getattr(record, head)))
            elif head == 'password':
                # We include a blank password column in the export so that
                # the import & export sheets have the same format.
                data.append('')
            elif head == 'service__id':
                service = record.service
                if service.id:
                    data.append(service.id)
                else:
                    data.append(service.name_en)
            # Times?
            elif isinstance(getattr(record, head, None), time):
                t = getattr(record, head)
                data.append(t.strftime("%H:%M"))
            # Get a value from a record pointed to by a foreign key
            elif '__' in head:
                field_name, next_field_name = head.split('__', 1)
                field = getattr(record, field_name)
                if field:
                    next_field = getattr(field, next_field_name, '')
                    data.append(next_field)
                else:
                    data.append('')
            else:
                data.append(getattr(record, head))

        write_row(sheet, row, data)
        row += 1


def write_row(sheet, row_number, data):
    """
    Given an xlwt Worksheet, a (0-based) row number, and an iterable
    of values, write the values into the cells of the row, starting
    at the first column and going across one cell per value.
    """
    col = 0
    for value in data:
        sheet.write(row_number, col, value)
        col += 1


def validate_and_import_data(user, data):
    """
    Given a user and bytes containing an Excel workbook, validate the content of the workbook, and
    the authorization of the user to submit the data in the workbook as an
    import.  If anything fails, raises a ValidationError whose errors
    dictionary will have all the errors detected.
    """
    errs = defaultdict(list)

    try:
        book = open_workbook(file_contents=data, on_demand=True, ragged_rows=False)
    except XLRDError:
        logger.exception("Error opening uploaded file as spreadsheet")
        errs['file'].append(
            _("Unable to open spreadsheet file; is it an Excel spreadsheet?"))
        return errs
    return validate_and_import_book(user, book)


def converted_errors(errs_by_sheet_row):
    # Convert errors for returning
    if errs_by_sheet_row:
        # Convert to a list of messages
        errs = []
        errs_by_sheet_row = dict(errs_by_sheet_row)
        for sheet_name in errs_by_sheet_row.keys():
            errs.append(_("Errors in sheet %s:") % sheet_name)
            for row_num, row_errs in errs_by_sheet_row[sheet_name].items():
                # The form validation errors each end with a period already, so we don't
                # need to insert any more punctuation between then.
                msgs = []
                for field, message in row_errs:
                    if field:
                        msgs.append("%s: %s" % (field, message))
                    else:
                        msgs.append(message)
                msg = " ".join(msgs)
                if row_num:
                    # Internal row numbers are 0-based, displayed row numbers are 1-based
                    msg = _("Row %d") % (1 + row_num) + ": " + msg
                errs.append(msg)
        return errs


@transaction.atomic()
def validate_and_import_book(user, book):
    """
    Given a user and an Excel workbook object, validate the content
    of the workbook, and
    the authorization of the user to submit the data in the workbook as an
    import.  If anything fails, returns a list of error messages.
    """

    errs_by_sheet_row = defaultdict(lambda: defaultdict(list))

    def add_error(sheet, rownum, field, message):
        sheet_name = sheet.name if sheet else ''
        errs_by_sheet_row[sheet_name][rownum].append((field, message))

    def add_form_errors(form):
        for fieldname, errors in form.errors.as_data().items():
            for error in errors:
                # each error is a Django ValidationError with a list of errors
                for message in error:
                    # print("message = %r (%s)" % (message, type(message)))
                    add_error(sheet, rownum, fieldname, message)

    providers = valid_providers_for_user(user)
    valid_provider_ids = set([provider.id for provider in providers])

    # imported_providers = []

    if book.nsheets != 3:
        add_error(None, 0, None,
                  _('Spreadsheet file should contain 3 sheets, this one has %d') % book.nsheets)
        return converted_errors(errs_by_sheet_row)

    is_staff = user.is_staff

    # Providers in first sheet
    sheet = book.sheet_by_index(0)
    headers = []
    if not sheet.nrows:
        add_error(sheet, 0, None,
                  _('First sheet has no data.'))
    else:
        headers = sheet.row_values(0)
    if sheet.name != PROVIDER_SHEET_NAME:
        add_error(sheet, 0, None,
                  _('First sheet has wrong name, expected {expected}, got {actual}').format(
                      expected=PROVIDER_SHEET_NAME, actual=sheet.name))
    elif headers != PROVIDER_HEADINGS:
        add_error(sheet, 0, None,
                  _('First sheet has wrong headers, expected %s') % PROVIDER_HEADINGS)
    elif headers:
        for rownum in range(1, sheet.nrows):
            values = sheet.row_values(rownum)
            # If they blanked all but the first column, they want the record deleted
            delete_provider = not any([value for value in values[1:]])
            data = dict(zip(headers, values))
            if not delete_provider:
                # number_of_monthly_beneficiaries is an int, but apparently
                # Excel only does floats...
                data['number_of_monthly_beneficiaries'] \
                    = int(data['number_of_monthly_beneficiaries'])
            provider_id = data['id']
            if not is_staff and provider_id and provider_id not in valid_provider_ids:
                if delete_provider:
                    add_error(sheet, rownum, 'provider',
                              _('%d is not a provider this user may delete') % provider_id)
                else:
                    add_error(sheet, rownum, 'provider',
                              _('%d is not a provider this user may import') % provider_id)
                continue
            if not is_staff and delete_provider:
                add_error(sheet, rownum, 'provider',
                          _('Only staff may delete providers'))
                continue
            if not data['id'] and not is_staff:
                # Trying to create a new one?
                add_error(sheet, rownum, 'provider',
                          _('Non-staff users may not create new providers'))
                continue

            provider_id = data.pop('id')
            if provider_id:
                try:
                    provider_id = int(provider_id)
                except ValueError:
                    add_error(sheet, rownum, 'id',
                              _('%s is not a valid ID' % provider_id))
                    continue
                try:
                    instance = Provider.objects.get(id=provider_id)
                except Provider.DoesNotExist:
                    add_error(sheet, rownum, 'provider',
                              _("There is no provider with id=%s") % provider_id)
                    continue
                else:
                    if delete_provider:
                        instance.delete()
                        continue
            else:
                instance = None
            password = data.pop('password')
            form = ProviderForm(data=data, instance=instance)
            if form.is_valid():
                instance = form.save()
                if password:
                    instance.user.set_password(password)
                    instance.user.save()
            else:
                add_form_errors(form)

    # Services in second sheet
    sheet = book.sheet_by_index(1)
    headers = []
    imported_services = []
    imported_services_by_id = {}
    imported_services_by_name = {}

    if not sheet.nrows:
        add_error(sheet, 0, None,
                  _('Second sheet has no data.'))
    else:
        headers = sheet.row_values(0)
    if sheet.name != SERVICES_SHEET_NAME:
        add_error(sheet, 0, None,
                  _('Second sheet has wrong name, expected {expected}, got {actual}').format(
                      expected=SERVICES_SHEET_NAME, actual=sheet.name))
    elif headers:
        valid_service_ids = set(Service.objects.filter(provider__in=providers)
                                .values_list('id', flat=True))
        for rownum in range(1, sheet.nrows):
            values = sheet.row_values(rownum)

            # If they blanked all but the first column, they want the service deleted
            delete_service = values[0] != '' and not any([value for value in values[1:]])

            data = dict(zip(headers, values))
            data['row'] = rownum
            service_id = data.pop('id')
            instance = None
            if not is_staff and service_id and service_id not in valid_service_ids:
                if delete_service:
                    add_error(sheet, rownum, 'service',
                              _('%d is not a service this user may delete') % service_id)
                else:
                    add_error(sheet, rownum, 'service',
                              _('%d is not a service this user may import') % service_id)
                continue

            if service_id:
                try:
                    service_id = int(service_id)
                except ValueError:
                    add_error(sheet, rownum, 'id',
                              _('%s is not a valid ID' % service_id))
                    continue
                try:
                    instance = Service.objects.get(id=service_id)
                except Service.DoesNotExist:
                    add_error(sheet, rownum, 'id', _('No service with id=%s') % service_id)
                    continue

            if delete_service:
                instance.delete()
                continue

            if not service_id and not is_staff and data['provider__id'] not in valid_provider_ids:
                add_error(sheet, rownum, 'provider__id',
                          _('Non-staff users may not create services for other providers'))
                continue

            # Okay so far
            form = ServiceForm(instance=instance, data=data)
            if not form.is_valid():
                add_form_errors(form)
            else:
                service = form.save()
                imported_services.append(service)
                imported_services_by_id[service.id] = service
                imported_services_by_name[service.name_en] = service

    # Selection criteria
    sheet = book.sheet_by_index(2)
    headers = []
    if not sheet.nrows:
        add_error(sheet, 0, None,
                  _('Second sheet has no data.'))
    else:
        headers = sheet.row_values(0)
    if sheet.name != SELECTION_CRITERIA_SHEET_NAME:
        add_error(sheet, 0, None,
                  _('Third sheet has wrong name, expected {expected}, got {actual}').format(
                      expected=SELECTION_CRITERIA_SHEET_NAME, actual=sheet.name))
    elif headers:
        for rownum in range(1, sheet.nrows):
            values = sheet.row_values(rownum)
            # If they blanked all but the first column, they want the record deleted
            delete_record = not any([value for value in values[1:]])
            data = dict(zip(headers, values))

            crit_id = data.pop('id')
            if crit_id:
                try:
                    crit_id = int(crit_id)
                except ValueError:
                    add_error(sheet, rownum, 'id',
                              _('%s is not a valid ID' % crit_id))
                    continue
                try:
                    instance = SelectionCriterion.objects.get(id=crit_id)
                except SelectionCriterion.DoesNotExist:
                    add_error(sheet, rownum, 'id',
                              _('No selection criterion with id = %s') % crit_id)
                    continue
                if delete_record:
                    # They wanted to delete it
                    instance.delete()
                    continue
            else:
                instance = None

            data['row'] = rownum
            service_id = data['service__id']
            try:
                service_id = int(service_id)
            except ValueError:
                service = imported_services_by_name.get(service_id, None)
            else:
                service = imported_services_by_id.get(service_id, None)
            if not service:
                add_error(sheet, rownum, 'service__id',
                          _("Selection criterion refers to service with ID or name {name!r} "
                            "that is not in the 2nd sheet. Choices: {list1!r} or {list2!r}").format(
                              name=service_id, list1=imported_services_by_name,
                              list2=imported_services_by_id
                          ))
                continue

            data['service'] = service.id
            form = SelectionCriterionForm(data=data, instance=instance)
            if form.is_valid():
                form.save()
            else:
                add_form_errors(form)

    return converted_errors(errs_by_sheet_row)
