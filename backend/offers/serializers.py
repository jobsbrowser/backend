from rest_framework.relations import StringRelatedField
from rest_framework.serializers import ModelSerializer

from offers.models import Offer, Tag, TagOfferRelationship


class TwoWayStringRelatedField(StringRelatedField):
    def to_internal_value(self, value):
        print(value)
        return value

class OfferSerializer(ModelSerializer):
    tags = TwoWayStringRelatedField(many=True)

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        offer = Offer.objects.create(**validated_data)
        for tag_name in tags:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            TagOfferRelationship.objects.create(tag=tag, offer=offer)
        return offer

    class Meta:
        model = Offer
        fields = '__all__'
