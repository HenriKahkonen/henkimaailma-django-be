from rest_framework import serializers
from .models import ChangelogEntry, ChangelogEntryTranslation

class ChangelogEntryTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangelogEntryTranslation
        fields = ["language","translated_title","body_markdown"]

class ChangelogEntrySerializer(serializers.ModelSerializer):
    translations = ChangelogEntryTranslationSerializer(many=True, read_only=True)
    class Meta:
        model = ChangelogEntry
        fields = ["id","date","title","translations"]