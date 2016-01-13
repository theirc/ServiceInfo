from django.conf.urls import url

from .views import update_page_rating, page_ratings
from services.views import service_detail_view


urlpatterns = [
    url(r'^update-page-rating/', update_page_rating, name='update-page-rating'),
    url(r'^page-ratings/', page_ratings, name='page-ratings'),
    url(r'(?P<service_id>\d+)/service$', service_detail_view, name='service-details'),
]
