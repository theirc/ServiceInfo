from django.conf.urls import include, url

from .views import update_page_rating


urlpatterns = [
    url(r'^update-page-rating/', 'update_page_rating', name='update-page-rating'),
]
