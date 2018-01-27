from collections import OrderedDict
from datetime import datetime, timedelta, date
from itertools import accumulate

from django.conf import settings
from django.db.models import Count
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from offers.filters import OffersFilter, SimpleOffersFilter
from offers.models import Offer, Tag
from offers.pagination import InfiniteScrollPagination
from offers.serializers import OfferSerializer


class OffersListView(ListAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    filter_class = OffersFilter
    pagination_class = InfiniteScrollPagination

    renderer_classes = (JSONRenderer,)

    def paginate_queryset(self, queryset):
        if "export" in self.request.GET:
            return None
        else:
            return super().paginate_queryset(queryset)

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if "export" in self.request.GET:
            response[
                'Content-Disposition'] = 'attachment; filename="offers.json"'
        return response


class OffersStatsView(GenericAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    filter_class = SimpleOffersFilter

    def get(self, request, *args, **kwargs):
        selected_offers = self.filter_offers_for_stats(
            self.filter_queryset(self.get_queryset())
        )
        all_offers = self.filter_offers_for_stats(
            self.get_queryset()
        )
        dates = self.get_days_range()

        selected_offers_count = self.calc_offers_count(selected_offers, dates)
        all_offers_count = self.calc_offers_count(all_offers, dates)
        percentage_offers_count = [
            (a / b) * 100 for a, b in zip(
                selected_offers_count, all_offers_count
            )
        ]
        return Response({
            "dates": dates,
            "offer_count": selected_offers_count,
            "offer_percentage": percentage_offers_count,
            "employers": self.calc_employers(selected_offers)
        })

    @staticmethod
    def get_days_range():
        start_date = settings.SHOW_STATS_FROM
        today = datetime.today().date()
        return [
            start_date + timedelta(days=i)
            for i in range((today - start_date).days + 1)
        ]

    @staticmethod
    def filter_offers_for_stats(qs):
        today = datetime.today().date()
        return qs.filter(
            date_posted__lte=today,
            valid_through__gte=settings.SHOW_STATS_FROM
        )

    @staticmethod
    def calc_offers_count(offers, dates):
        buckets = OrderedDict((date, 0) for date in dates)
        start_date = dates[0]
        end_date = dates[-1]
        for offer in offers:
            key_to_increment = max(start_date, offer.date_posted)
            buckets[key_to_increment] += 1
            if offer.valid_through < end_date:
                buckets[offer.valid_through + timedelta(days=1)] -= 1
        return list(accumulate(buckets.values()))

    @staticmethod
    def calc_employers(offers):
        employers = {}
        for offer in offers:
            counter = employers.get(offer.employer, 0)
            employers[offer.employer] = counter + 1

        return [
            {"name": name, "count": count} for name, count
            in sorted(employers.items(), key=lambda tuple: -tuple[1])
        ][:10]


class SystemInfoView(GenericAPIView):
    queryset = Offer.objects.all()

    def get(self, request, *args, **kwargs):
        dates = OffersStatsView.get_days_range()
        return Response({
            "days": dates,
            "offers_count": self.calc_offers_count(dates),
            "offers_number": self.queryset.count(),
            "last_crawl_date": date.today(),
        })

    def calc_offers_count(self, dates):
        dates_posted = iter(
            self.get_queryset().order_by('date_posted').values(
                'date_posted').annotate(posted_this_day=Count('date_posted'))
        )
        offers_count = []
        total = 0
        item = None
        end_of_iterator = False
        for date in dates:
            if not end_of_iterator:
                while item is None or item['date_posted'] <= date:
                    try:
                        item = next(dates_posted)
                    except StopIteration:
                        end_of_iterator = True
                        break
                    else:
                        total += item['posted_this_day']
            offers_count.append(total)
        return offers_count


@api_view(['GET'])
def tags_list_view(request):
    return Response(
        Tag.objects.order_by('name').values_list('name', flat=True)
    )
