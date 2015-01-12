import factory
import factory.fuzzy
from email_user.tests.factories import EmailUserFactory

from services.models import Provider


class ProviderFactory(factory.DjangoModelFactory):
    class Meta:
        model = Provider

    name = factory.fuzzy.FuzzyText()
    type = Provider.PROVIDER_TYPE_1
    description = factory.fuzzy.FuzzyText()
    user = factory.SubFactory(EmailUserFactory)
