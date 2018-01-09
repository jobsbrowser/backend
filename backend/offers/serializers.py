from rest_framework.relations import StringRelatedField
from rest_framework.serializers import ModelSerializer

from offers.models import Offer


class OfferSerializer(ModelSerializer):
    tags = StringRelatedField(many=True)

    class Meta:
        model = Offer
        fields = '__all__'
