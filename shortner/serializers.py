from rest_framework import serializers
from .models import ShortURL


class ShortURLSerializer(serializers.ModelSerializer):
    long_url = serializers.URLField()

    class Meta:
        model = ShortURL
        fields = ["long_url"]