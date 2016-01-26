from django.conf.urls import url

from .views import service_detail_view


urlpatterns = [
    url(r'service/(?P<service_id>\d+)/$', service_detail_view, name='backend-service-detail'),
]
