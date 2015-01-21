import factory
import factory.fuzzy
from email_user.tests.factories import EmailUserFactory

from services.models import Provider, ProviderType


class ProviderTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = ProviderType

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
