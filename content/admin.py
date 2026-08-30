from django.contrib import admin, messages
from django import forms
from .models import SoundsAndScapesPack, SoundsAndScapesPackDescription, SnSChangelogEntry, SnSChangelogEntryTranslation, MusicRelease, MusicReleaseTranslation, Video, VideoTranslation, Article, ArticleTranslation, ChangelogEntry, ChangelogEntryTranslation
from .widgets import TagWidget

### Custom admin actions ###

@admin.action(description="Mark selected entries as published")
def make_published(modeladmin, request, queryset):
    updated = queryset.update(published=True)
    modeladmin.message_user(
        request,
        f"{updated} entr{'y' if updated == 1 else 'ies'} marked as published.",
        messages.SUCCESS,
    )


@admin.action(description="Mark selected entries as unpublished")
def make_unpublished(modeladmin, request, queryset):
    updated = queryset.update(published=False)
    modeladmin.message_user(
        request,
        f"{updated} entr{'y' if updated == 1 else 'ies'} marked as unpublished.",
        messages.SUCCESS,
    )

### SNS PACKS ADMIN ###

class SnSReleaseForm(forms.ModelForm):
    class Meta:
        model = SoundsAndScapesPack
        fields = "__all__"
        widgets = {"tags" : TagWidget}

class SnsPackDescInline(admin.TabularInline):
    '''Language-specific description of a SnS sample pack.'''
    model = SoundsAndScapesPackDescription
    extra = 1

@admin.register(SoundsAndScapesPack)
class SnSPackAdmin(admin.ModelAdmin):
    form = SnSReleaseForm
    inlines = [SnsPackDescInline]
    list_display = ("title", "release_date", "updated_date", "published", "likes")
    list_filter = ("published",)
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}
    actions = [make_published, make_unpublished]

class SnSChangelogEntryTranslationInline(admin.TabularInline):
    model = SnSChangelogEntryTranslation
    extra = 1

@admin.register(SnSChangelogEntry)
class SnSChangelogEntryAdmin(admin.ModelAdmin):
    inlines = [SnSChangelogEntryTranslationInline]
    list_display = ("date", "title", "published")
    list_filter = ("published",)
    search_fields = ("title", "body_markdown", "tags")
    actions = [make_published, make_unpublished]

### MUSIC RELEASES ADMIN ###

class MusicReleaseForm(forms.ModelForm):
    class Meta:
        model = MusicRelease
        fields = "__all__"
        widgets = {"tags" : TagWidget}

class MusicReleaseTranslationInline(admin.TabularInline):
    model = MusicReleaseTranslation
    extra = 1

@admin.register(MusicRelease)
class MusicReleaseAdmin(admin.ModelAdmin):
    form = MusicReleaseForm
    inlines = [MusicReleaseTranslationInline]
    list_display = ("title", "release_date", "published")
    list_filter = ("published",)
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}
    actions = [make_published, make_unpublished]

### VIDEOS ADMIN ###

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = "__all__"
        widgets = {"tags" : TagWidget}

class VideoTranslationInLine(admin.TabularInline):
    model = VideoTranslation
    extra = 1

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    form = VideoForm
    inlines = [VideoTranslationInLine]
    list_display = ("internal_title", "youtube_id", "published_date", "published")
    list_filter = ("published",)
    search_fields = ("internal_title", "youtube_id", "category")
    actions = [make_published, make_unpublished]

### ARTICLES ADMIN ###

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = "__all__"
        widgets = {"tags" : TagWidget}

class ArticleTranslationInline(admin.TabularInline):
    model = ArticleTranslation
    extra = 1

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    form = ArticleForm
    inlines = [ArticleTranslationInline]
    list_display = ("title", "published_date", "updated_at", "published", "category", "external_url")
    list_filter = ("published",)
    search_fields = ("title", "summary","category")
    #TODO: check if search_fields = ("body_markdown") works
    prepopulated_fields = {"slug": ("title",)}
    actions = [make_published, make_unpublished]

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
    actions = [make_published, make_unpublished]