from django.conf.urls import url

from services.views import service_detail_view
from .views import update_page_rating


urlpatterns = [
    url(r'^update-page-rating/', update_page_rating, name='update-page-rating'),
    url(r'(?P<service_id>\d+)/service$', service_detail_view, name='service-details'),
]
