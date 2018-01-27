import json
from datetime import datetime

from django.core.management.base import BaseCommand

from offers.models import Offer, TagOfferRelationship, Tag


class Command(BaseCommand):
    """
    Create Offers and Tags using MongoDB dump.
    Each line in log file should be serialized offer - valid JSON
    """

    def add_arguments(self, parser):
        parser.add_argument(
            'offers_file', type=str, help="Path to file containing offers lines")

    def handle(self, *args, **options):
        with open(options['offers_file']) as f:
            offers_list = []
            tags_set = set()
            offers_tags = {}

            print("Parsing...")
            for i, line in enumerate(f):
                item = json.loads(line)
                if not 'tags' in item:
                    continue
                offers_tags[item['offer_id']] = item.pop("tags")
                item['date_posted'] = datetime.strptime(item['date_posted'], '%Y-%m-%d').date()
                item['valid_through'] = datetime.strptime(item['valid_through'], '%Y-%m-%d').date()
                for unnecessary_key in ['_id', 'timestamp', 'categories', 'category', 'category_name']:
                    item.pop(unnecessary_key, None)
                offer = Offer(**item)
                offers_list.append(offer)
                for tag in offers_tags[item['offer_id']]:
                    tags_set.add(tag)

            print("Saving...")
            saved_offers = Offer.objects.bulk_create(offers_list)
            offers_map = {offer.offer_id: offer for offer in Offer.objects.all()}
            print(f"{len(offers_list)} offers saved.")

            saved_tags = Tag.objects.bulk_create(Tag(name=tag) for tag in tags_set)
            tags_map = {tag.name: tag for tag in Tag.objects.all()}
            print(f"{len(tags_set)} tags saved.")

            print("Creating relationships...")
            relationships = []
            for offer_id, offer in offers_map.items():
                for tag_name in offers_tags[offer_id]:
                    relationships.append(TagOfferRelationship(
                        offer_id=offer.pk, tag_id=tags_map[tag_name].pk
                    ))
            TagOfferRelationship.objects.bulk_create(relationships)
            print("Done")
