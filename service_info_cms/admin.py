from django.contrib import admin
from cms.extensions import PageExtensionAdmin

from .models import IconNameExtension, RatingExtension, SocialMediaExtension, PageRating


class IconNameExtensionAdmin(PageExtensionAdmin):
    pass


class RatingExtensionAdmin(PageExtensionAdmin):
    pass


class SocialMediaExtensionAdmin(PageExtensionAdmin):
    pass


class PageRatingAdmin(admin.ModelAdmin):
    list_display = ('page_obj', 'num_ratings', 'average_rating',)
    readonly_fields = ('page_obj', 'num_ratings', 'average_rating', 'rating_total')
    list_filter = ('average_rating', )
    search_fields = ()
    ordering = ('page_obj', 'num_ratings', 'average_rating', '-num_ratings', '-average_rating', )


admin.site.register(IconNameExtension, IconNameExtensionAdmin)
admin.site.register(RatingExtension, RatingExtensionAdmin)
admin.site.register(SocialMediaExtension, SocialMediaExtensionAdmin)
admin.site.register(PageRating, PageRatingAdmin)
