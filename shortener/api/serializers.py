from rest_framework import serializers
from shortener.models import ShortURL
from shortener.utils import check_short_url, generate_short_url
from shortener.utils import ShortURLGenerationError

class ShortURLSerializer(serializers.ModelSerializer):
    short_url = serializers.CharField(required=False)

    class Meta:
        model = ShortURL
        fields = ['short_url', 'long_url']

    def validate_short_url(self, value):
        if value:
            check_short_url(value)
        return value

    def create(self, validated_data):
        try:
            cleaned_short_url = validated_data.get('short_url')
            validated_data['short_url'] = generate_short_url(cleaned_short_url)
        except ShortURLGenerationError as e:
            raise serializers.ValidationError({"short_url": str(e)})
        
        return ShortURL.objects.create(**validated_data)