import random
import string

import factory
import factory.fuzzy
from email_user.tests.factories import EmailUserFactory

from services.models import Provider, ProviderType, SelectionCriterion, Service, ServiceArea, \
    ServiceType, Feedback, Nationality


class FuzzyURL(factory.fuzzy.BaseFuzzyAttribute):
    """Random URL"""
    def fuzz(self):
        chars = ''.join([random.choice(string.ascii_lowercase) for _i in range(10)])
        return 'http://www.%s.com' % chars


class FuzzyLocation(factory.fuzzy.BaseFuzzyAttribute):
    """random geographic location"""
    def fuzz(self):
        longitude = random.uniform(-180.0, 180.0)
        latitude = random.uniform(-90.0, 90.0)
        return "POINT( %f %f )" % (longitude, latitude)


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
    number_of_monthly_beneficiaries = factory.fuzzy.FuzzyInteger(0, 999999)
    phone_number = factory.LazyAttribute(create_valid_phone_number)
    website = FuzzyURL()
    focal_point_name_en = factory.fuzzy.FuzzyText()
    focal_point_name_ar = factory.fuzzy.FuzzyText()
    focal_point_name_fr = factory.fuzzy.FuzzyText()
    focal_point_phone_number = factory.LazyAttribute(create_valid_phone_number)
    address_en = factory.fuzzy.FuzzyText()
    address_ar = factory.fuzzy.FuzzyText()
    address_fr = factory.fuzzy.FuzzyText()


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
    location = FuzzyLocation()
    cost_of_service = factory.fuzzy.FuzzyText()


class SelectionCriterionFactory(factory.DjangoModelFactory):
    class Meta:
        model = SelectionCriterion

    text_en = factory.fuzzy.FuzzyText()
    text_ar = factory.fuzzy.FuzzyText()
    text_fr = factory.fuzzy.FuzzyText()
    service = factory.SubFactory(ServiceFactory)


# I'm a bit surprised at having to write all this boilerplate code,
# but I didn't see anything in FactoryBoy that would do it for us.
# Somebody clue me in if I'm missing something, please.
def random_boolean():
    return random.choice([False, True])


def random_nationality():
    return random.choice(Nationality.objects.all())


def random_service_area():
    return random.choice(ServiceArea.objects.all())


def get_random_value_for_choice_field(field_name):
    field = Feedback._meta.get_field(field_name)
    choices = [value for value, name in field.get_flatchoices(include_blank=False)]
    return random.choice(choices)


def random_difficulty_contacting():
    return get_random_value_for_choice_field('difficulty_contacting')


def random_non_delivery_explained():
    return get_random_value_for_choice_field('non_delivery_explained')


def get_wait_time(stub):
    if stub.delivered:
        return get_random_value_for_choice_field('wait_time')


def get_wait_time_satisfaction(stub):
    if stub.delivered:
        return random.randint(1, 5)


def get_quality(stub):
    if stub.delivered:
        return random.randint(1, 5)


def get_other_difficulties(stub):
    if stub.difficulty_contacting == 'other':
        chars = [random.choice(string.ascii_letters) for _i in range(10)]
        return ''.join(chars)
    return ''


class FeedbackFactory(factory.DjangoModelFactory):
    class Meta:
        model = Feedback

    delivered = factory.fuzzy.FuzzyAttribute(random_boolean)
    nationality = factory.fuzzy.FuzzyAttribute(random_nationality)
    staff_satisfaction = factory.fuzzy.FuzzyInteger(1, 5)
    area_of_residence = factory.fuzzy.FuzzyAttribute(random_service_area)
    service = factory.SubFactory(ServiceFactory)
    non_delivery_explained = factory.fuzzy.FuzzyAttribute(random_non_delivery_explained)
    name = factory.fuzzy.FuzzyText()
    phone_number = factory.LazyAttribute(create_valid_phone_number)
    difficulty_contacting = factory.fuzzy.FuzzyAttribute(random_difficulty_contacting)

    # These only have to be set if delivered is True
    quality = factory.LazyAttribute(get_quality)
    wait_time = factory.LazyAttribute(get_wait_time)
    wait_time_satisfaction = factory.LazyAttribute(get_wait_time_satisfaction)

    # This only has to be set if difficulty_contacting was 'other'
    other_difficulties = factory.LazyAttribute(get_other_difficulties)
