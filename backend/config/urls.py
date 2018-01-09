from django.conf.urls import url

from offers.views import OffersListView, OffersStatsView, SystemInfoView

urlpatterns = [
    url(r'^info/$', SystemInfoView.as_view(), name='info'),
    url(r'^offers/$', OffersListView.as_view(), name='offers'),
    url(r'^offers/stats/$', OffersStatsView.as_view(), name='stats'),
]
