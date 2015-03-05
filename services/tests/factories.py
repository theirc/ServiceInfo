import random
import string

import factory
import factory.fuzzy
from email_user.tests.factories import EmailUserFactory

from services.models import Provider, ProviderType, SelectionCriterion, Service, ServiceArea, \
    ServiceType


class FuzzyURL(factory.fuzzy.BaseFuzzyAttribute):
    """Random URL"""
    def fuzz(self):
        chars = ''.join([random.choice(string.ascii_lowercase) for _i in range(10)])
        return 'http://www.%s.com' % chars


class ProviderTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = ProviderType

    number = factory.Sequence(lambda n: n)
    name_en = factory.fuzzy.FuzzyText()
    name_ar = factory.fuzzy.FuzzyText()
    name_fr = factory.fuzzy.FuzzyText()


def create_valid_phone_number(stub):
    # Valid Lebanon phone number, ##-######
    chars = string.digits
    prefix = ''.join([random.choice(chars) for _i in range(2)])
    suffix = ''.join([random.choice(chars) for _i in range(6)])
    return "%s-%s" % (prefix, suffix)


class ProviderFactory(factory.DjangoModelFactory):
    class Meta:
        model = Provider

    name_en = factory.fuzzy.FuzzyText()
    name_ar = factory.fuzzy.FuzzyText()
    name_fr = factory.fuzzy.FuzzyText()
    type = factory.SubFactory(ProviderTypeFactory)
    description_en = factory.fuzzy.FuzzyText()
    description_ar = factory.fuzzy.FuzzyText()
    description_fr = factory.fuzzy.FuzzyText()
    user = factory.SubFactory(EmailUserFactory)
    number_of_monthly_beneficiaries = 0
    phone_number = factory.LazyAttribute(create_valid_phone_number)
    website = FuzzyURL()


class ServiceTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = ServiceType

    number = factory.Sequence(lambda n: n)
    name_en = factory.fuzzy.FuzzyText()
    name_ar = factory.fuzzy.FuzzyText()
    name_fr = factory.fuzzy.FuzzyText()
    comments_en = factory.fuzzy.FuzzyText()
    comments_ar = factory.fuzzy.FuzzyText()
    comments_fr = factory.fuzzy.FuzzyText()


class ServiceAreaFactory(factory.DjangoModelFactory):
    class Meta:
        model = ServiceArea

    name_en = factory.fuzzy.FuzzyText()
    name_ar = factory.fuzzy.FuzzyText()
    name_fr = factory.fuzzy.FuzzyText()


class ServiceFactory(factory.DjangoModelFactory):
    class Meta:
        model = Service

    provider = factory.SubFactory(ProviderFactory)
    name_en = factory.fuzzy.FuzzyText()
    name_ar = factory.fuzzy.FuzzyText()
    name_fr = factory.fuzzy.FuzzyText()
    description_en = factory.fuzzy.FuzzyText()
    description_ar = factory.fuzzy.FuzzyText()
    description_fr = factory.fuzzy.FuzzyText()
    additional_info_en = factory.fuzzy.FuzzyText()
    additional_info_ar = factory.fuzzy.FuzzyText()
    additional_info_fr = factory.fuzzy.FuzzyText()
    area_of_service = factory.SubFactory(ServiceAreaFactory)
    type = factory.SubFactory(ServiceTypeFactory)


class SelectionCriterionFactory(factory.DjangoModelFactory):
    class Meta:
        model = SelectionCriterion

    text_en = factory.fuzzy.FuzzyText()
    text_ar = factory.fuzzy.FuzzyText()
    text_fr = factory.fuzzy.FuzzyText()
    service = factory.SubFactory(ServiceFactory)
