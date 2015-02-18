import string

import factory
import factory.fuzzy
from email_user.tests.factories import EmailUserFactory

from services.models import Provider, ProviderType, SelectionCriterion, Service, ServiceArea, \
    ServiceType


class ProviderTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = ProviderType

    number = factory.Sequence(lambda n: n)
    name_en = factory.fuzzy.FuzzyText()
    name_ar = factory.fuzzy.FuzzyText()
    name_fr = factory.fuzzy.FuzzyText()


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
    phone_number = factory.fuzzy.FuzzyText(chars=string.digits)


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
    area_of_service = factory.SubFactory(ServiceAreaFactory)
    type = factory.SubFactory(ServiceTypeFactory)


class SelectionCriterionFactory(factory.DjangoModelFactory):
    class Meta:
        model = SelectionCriterion

    text_en = factory.fuzzy.FuzzyText()
    text_ar = factory.fuzzy.FuzzyText()
    text_fr = factory.fuzzy.FuzzyText()
    service = factory.SubFactory(ServiceFactory)
