import factory
import factory.fuzzy

from services.models import Provider


class ProviderFactory(factory.DjangoModelFactory):
    class Meta:
        model = Provider

    name = factory.fuzzy.FuzzyText()
    type = Provider.PROVIDER_TYPE_1
    description = factory.fuzzy.FuzzyText()
