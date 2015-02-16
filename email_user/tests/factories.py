import factory
from ..models import EmailUser


class EmailUserFactory(factory.DjangoModelFactory):
    class Meta:
        model = EmailUser

    email = factory.Sequence(lambda n: "user%d@example.com" % n)
    language = 'en'

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the default ``_create`` with our custom call."""
        manager = cls._get_manager(model_class)
        # The default would use ``manager.create(*args, **kwargs)``
        return manager.create_user(*args, **kwargs)
