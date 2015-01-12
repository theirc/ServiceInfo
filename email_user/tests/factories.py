import factory
from ..models import EmailUser


class EmailUserFactory(factory.DjangoModelFactory):
    class Meta:
        model = EmailUser

    email = factory.Sequence(lambda n: "user%d@example.com" % n)
