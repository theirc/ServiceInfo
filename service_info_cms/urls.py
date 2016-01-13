from django.conf.urls import url

from .views import update_page_rating, page_ratings


urlpatterns = [
    url(r'^update-page-rating/', update_page_rating, name='update-page-rating'),
    url(r'^page-ratings/', page_ratings, name='page-ratings'),
]
