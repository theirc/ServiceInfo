import factory
import factory.fuzzy
from email_user.tests.factories import EmailUserFactory

from services.models import Provider, ProviderType, Service, ServiceArea


class ProviderTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = ProviderType

    name_en = factory.fuzzy.FuzzyText()
    name_fr = factory.fuzzy.FuzzyText()
    name_ar = factory.fuzzy.FuzzyText()


class ProviderFactory(factory.DjangoModelFactory):
    class Meta:
        model = Provider

    name = factory.fuzzy.FuzzyText()
    type = factory.SubFactory(ProviderTypeFactory)
    description = factory.fuzzy.FuzzyText()
    user = factory.SubFactory(EmailUserFactory)
    number_of_monthly_beneficiaries = 0


class ServiceAreaFactory(factory.DjangoModelFactory):
    class Meta:
        model = ServiceArea

    name = factory.fuzzy.FuzzyText()


class ServiceFactory(factory.DjangoModelFactory):
    class Meta:
        model = Service

    provider = factory.SubFactory(ProviderFactory)
    name = factory.fuzzy.FuzzyText()
    description = factory.fuzzy.FuzzyText()
    area_of_service = factory.SubFactory(ServiceAreaFactory)
