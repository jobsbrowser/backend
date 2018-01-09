from django_filters.rest_framework import FilterSet, filters

from offers.models import Offer, Tag


class SimpleOffersFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        name="tags__name", to_field_name='name', conjoined=True
    )

    class Meta:
        model = Offer
        fields = ['tags']


class OffersFilter(SimpleOffersFilter):
    date_from = filters.DateFilter(name="valid_through", lookup_expr="gte")
    date_to = filters.DateFilter(name="date_posted", lookup_expr="lte")

    class Meta(SimpleOffersFilter.Meta):
        fields = SimpleOffersFilter.Meta.fields + ['date_from', 'date_to']
