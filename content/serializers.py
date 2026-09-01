from rest_framework import serializers
from .models import ChangelogEntry, ChangelogEntryTranslation, Tag, VideoTranslation, Video, ArticleTranslation, Article, SoundsAndScapesPack, SoundsAndScapesPackDescription, SnSChangelogEntry, SnSChangelogEntryTranslation

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["name"] # ["name", "slug"] if the frontend ever needs to display a page filtered by tags

###########################
## Changelog serializers ##
###########################

class ChangelogEntryTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangelogEntryTranslation
        fields = ["language","translated_title","body_markdown"]

class ChangelogEntrySerializer(serializers.ModelSerializer):
    translations = ChangelogEntryTranslationSerializer(many=True, read_only=True)
    class Meta:
        model = ChangelogEntry
        fields = ["id","date","title","translations"]

################################################
## Review summary (video/article) serializers ##
################################################

class VideoTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoTranslation
        fields = ["language", "translated_title", "description","translated_video_subtitles"]

class VideoReviewSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="internal_title")
    type = serializers.SerializerMethodField()
    ytid = serializers.CharField(source="youtube_id")
    tags = TagSerializer(many=True, read_only=True)
    extras = serializers.JSONField(source="video_extras")
    translations = VideoTranslationSerializer(many=True, read_only=True)

    class Meta:
        model = Video
        fields = ["title", "type", "content_language", "description", "category", "rating", "ytid", "published_date", "tags", "slug", "likes", "extras", "translations"]

    def get_type(self, obj):
        return "V"


class ArticleTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleTranslation
        fields = ["language", "translated_title", "description"]

class ArticleReviewSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    imgUrl = serializers.URLField(source="article_image_url")
    tags = TagSerializer(many=True, read_only=True)
    extras = serializers.JSONField(source="article_extras")
    translations = ArticleTranslationSerializer(many=True, read_only=True)
    full_translations = serializers.SerializerMethodField()
    e_url = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ["title", "type", "content_language", "description", "category", "rating", "imgUrl", "e_url", "published_date", "tags", "slug", "likes", "extras", "translations","full_translations"]

    def get_type(self, obj):
        return "E" if obj.external_url else "A"

    def get_e_url(self, obj):
        return obj.external_url or None

    def get_full_translations(self, obj):
        """
        Returns a list of language codes for translations that have non-empty values
        for translated_title, description, ingress, and body_markdown.
        """
        full_langs = []
        for translation in obj.translations.all():
            if all([
                translation.translated_title,
                translation.description,
                translation.ingress,
                translation.body_markdown,
            ]):
                full_langs.append(translation.language)
        return full_langs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data.get("e_url"):
            data.pop("e_url", None)
        return data

##################################################
## Review full data (video/article) serializers ##
##################################################


class VideoDetailSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="internal_title")
    type = serializers.SerializerMethodField()
    ytid = serializers.CharField(source="youtube_id")
    tags = TagSerializer(many=True, read_only=True)
    extras = serializers.JSONField(source="video_extras")
    translations = VideoTranslationSerializer(many=True, read_only=True)

    class Meta:
        model = Video
        fields = [
            "title", "type", "ytid", "description", "category", "rating", "content_language",
            "published_date", "tags", "slug", "likes", "extras", "translations",
        ]

    def get_type(self, obj):
        return "V"

class ArticleTranslationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleTranslation
        fields = ["language", "translated_title", "ingress", "description", "body_markdown"]


class ArticleDetailSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    imgUrl = serializers.URLField(source="article_image_url")
    tags = TagSerializer(many=True, read_only=True)
    extras = serializers.JSONField(source="article_extras")
    translations = ArticleTranslationDetailSerializer(many=True, read_only=True)
    e_url = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "title", "type", "content_language", "ingress", "body_markdown", "description", "imgUrl", "e_url", "category", "rating",
            "published_date", "tags", "slug", "likes", "extras", "translations",
        ]

    def get_type(self, obj):
        return "E" if obj.external_url else "A"

    def get_e_url(self, obj):
        return obj.external_url or None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data.get("e_url"):
            data.pop("e_url", None)
        return data

class SnSChangelogEntryTranslationSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    class Meta:
        model = SnSChangelogEntryTranslation
        fields = ["language","title","body_markdown", "tags"]

class SnSChangelogSerializer(serializers.ModelSerializer):
    translations = SnSChangelogEntryTranslationSerializer(many=True, read_only=True)

    class Meta:
        model = SnSChangelogEntry
        fields = ["date", "title", "translations"]

class SnSSamplePackTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoundsAndScapesPackDescription
        fields = ["language", "description"]

class SnSSamplePackSerializer(serializers.ModelSerializer):
    imgUrl = serializers.URLField(source="cover_image_url")
    e_url = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    file_list = serializers.JSONField()
    translations = SnSSamplePackTranslationSerializer(many=True, read_only=True)
    release_date = serializers.DateField()
    updated_date = serializers.DateField()

    class Meta:
        model = SoundsAndScapesPack
        fields = [
            "title", "slug", "imgUrl", "e_url", "tags",
            "release_date", "updated_date", "likes", "translations", "file_list"
        ]

    def get_e_url(self, obj):
        return obj.external_url or None