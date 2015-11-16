from django.db import models

from cms.extensions import PageExtension
from cms.extensions.extension_pool import extension_pool
from aldryn_categories.fields import CategoryManyToManyField

class CategoryExtension(PageExtension):
    categories = CategoryManyToManyField()

extension_pool.register(CategoryExtension)
