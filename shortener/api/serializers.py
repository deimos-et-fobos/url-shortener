import re
from rest_framework import serializers
from shortener.models import ShortURL, SHORT_URL_MAX_LENGTH
from shortener.utils import check_short_url, generate_short_url, ShortURLGenerationError

class ShortURLSerializer(serializers.ModelSerializer):
    short_url = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = ShortURL
        fields = ['short_url', 'url']

    def validate_short_url(self, value):
        print('aqui')
        if value:
            if len(value) > SHORT_URL_MAX_LENGTH:
                raise serializers.ValidationError(f"Url must be at most {SHORT_URL_MAX_LENGTH} characters")
            if not re.fullmatch(r'[a-zA-Z0-9]+', value):
                raise serializers.ValidationError("Url can contain only numbers and letters")
            check_short_url(value)
        return value

    def create(self, validated_data):
        try:
            cleaned_short_url = validated_data.get('short_url')
            validated_data['short_url'] = generate_short_url(cleaned_short_url)
        except ShortURLGenerationError as e:
            raise serializers.ValidationError({"short_url": str(e)})
        
        return ShortURL.objects.create(**validated_data)