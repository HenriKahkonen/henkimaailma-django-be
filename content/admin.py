from django.contrib import admin
from .models import SoundsAndScapesPack, SoundsAndScapesPackTranslation, MusicRelease, MusicReleaseTranslation, Video, VideoTranslation, Article, ArticleTranslation, ChangelogEntry, ChangelogEntryTranslation

### SNS PACKS ADMIN ###

class SnsPackTranslationInline(admin.TabularInline):
    model = SoundsAndScapesPackTranslation
    extra = 1

@admin.register(SoundsAndScapesPack)
class SnSPackAdmin(admin.ModelAdmin):
    inlines = [SnsPackTranslationInline]
    list_display = ("title", "release_date", "published", "likes")
    list_filter = ("published",)
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}

### MUSIC RELEASES ADMIN ###

class MusicReleaseTranslationInline(admin.TabularInline):
    model = MusicReleaseTranslation
    extra = 1

@admin.register(MusicRelease)
class MusicReleaseAdmin(admin.ModelAdmin):
    inlines = [MusicReleaseTranslationInline]
    list_display = ("title", "release_date", "published")
    list_filter = ("published",)
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}

### VIDEOS ADMIN ###

class VideoTranslationInLine(admin.TabularInline):
    model = VideoTranslation
    extra = 1

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    inlines = [VideoTranslationInLine]
    list_display = ("title", "youtube_id", "published_date", "published")
    list_filter = ("published",)
    search_fields = ("title", "youtube_id", "category")

### ARTICLES ADMIN ###

class ArticleTranslationInline(admin.TabularInline):
    model = ArticleTranslation
    extra = 1

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    inlines = [ArticleTranslationInline]
    list_display = ("title", "published_date", "updated_at", "published", "article_category", "external_url")
    list_filter = ("published",)
    search_fields = ("title", "summary","article_category")
    #TODO: check if search_fields = ("body_markdown") works
    prepopulated_fields = {"slug": ("title",)}

### CHANGELOG ADMIN ###

class ChangelogEntryTranslationInline(admin.TabularInline):
    model = ChangelogEntryTranslation
    extra = 1

@admin.register(ChangelogEntry)
class ChangelogEntryAdmin(admin.ModelAdmin):
    inlines = [ChangelogEntryTranslationInline]
    list_display = ("date", "title", "published")
    list_filter = ("published",)
    search_fields = ("title", "body_markdown", "tags")