from django.contrib import admin
from django import forms
from .models import SoundsAndScapesPack, SoundsAndScapesPackDescription, MusicRelease, MusicReleaseTranslation, Video, VideoTranslation, Article, ArticleTranslation, ChangelogEntry, ChangelogEntryTranslation
from .widgets import TagWidget

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
    list_display = ("title", "release_date", "published", "likes")
    list_filter = ("published",)
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}

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