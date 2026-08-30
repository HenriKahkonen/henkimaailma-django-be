from django.db import models
from django.utils.text import slugify

# Documentation : https://docs.djangoproject.com/en/6.1/topics/db/models/

# /////////////////////////////////
# ///// Abstract base classes /////
# /////////////////////////////////

class PublishableModel(models.Model):
    """Adds draft/published staging + timestamps to any model."""
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class SluggedModel(models.Model):
    """Adds a slug field, auto-populated from `title` if left blank."""
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name

# ///////////////////////////////
# /// Constant specifications ///
# ///////////////////////////////

LANGUAGES = [
    ("fi", "Finnish"),
    ("en", "English"),
]

SNS_TAGS = [
    ("sfx","Sound effect"),
    ("instrument", "Instrument"),
    ("field_rec", "Field Recording"),
    ("drums","Drums"),
    ("perc", "Percussion"),
    ("melodic", "Melodic instrument"),
]

SNS_LICENCES = [
    ("cc0", "CC0 Creative Commons Licence"),
    ("all_rights_reserved","All rights reserved")
]

ARTICLE_CATEGORIES = [
    ("blog", "Blog post"), 
    ("game_review","Game review"),
    ("music_review","Music review"), 
    ("film_review","Film review"), 
    ("tv_review","TV review"), 
    ("project_writeup","Project writeup"),
]

YOUTUBE_VIDEO_CATEGORIES = [
    ("game_review","Game review"),
    ("music_review","Music review"),
    ("film_review","Film review"),
    ("tv_review","TV review"),
    ("video_essay","Video essay"),
    ("vlog","Vlog"),
    ("commentary","Commentary video"),
]


# ///////////////////////////////////////
# ///// Actually usable data models /////
# ///////////////////////////////////////


### SNS SAMPLE PACKS

class SoundsAndScapesPack(PublishableModel,SluggedModel):
    title = models.CharField(max_length=255)
    cover_image_url = models.URLField(blank=True)
    external_url = models.URLField(help_text="Link to where the sample pack is downloadable from")
    licence = models.CharField(max_length=255, choices=SNS_LICENCES,default="all_rights_reserved")
    tags = models.ManyToManyField(Tag, blank=True, related_name="sns_samplepacks")
    file_list = models.JSONField(default=dict, blank=True)
    release_date = models.DateField()
    updated_date = models.DateField()
    likes = models.IntegerField(default=0)

    class Meta:
        ordering = ["-release_date"]
        verbose_name_plural = "Sounds and Scapes -sample packs"

    def __str__(self):
        return self.title

class SoundsAndScapesPackDescription(models.Model):
    snspack = models.ForeignKey(SoundsAndScapesPack, related_name="translations", on_delete=models.CASCADE)
    language = models.CharField(max_length=3, choices=LANGUAGES)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ("snspack","language")
        verbose_name_plural = "Sounds and Scapes -sample pack translations"

    def __str__(self):
        return f"{self.snspack_id} [{self.language}]"

class SnSChangelogEntry(PublishableModel):
    date = models.DateField()
    title = models.CharField(max_length=255)

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Sounds and Scapes -changelog entries"

    def __str__(self):
        return f"{self.date} — {self.title}"

class SnSChangelogEntryTranslation(models.Model):
    changelog_entry = models.ForeignKey(SnSChangelogEntry, related_name="translations", on_delete=models.CASCADE)
    language = models.CharField(max_length=3, choices=LANGUAGES)
    body_markdown = models.TextField()
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated")

    class Meta:
        verbose_name_plural = "SnS Changelog Entries"
        unique_together = ("changelog_entry", "language")


### MUSIC RELEASES

class MusicRelease(PublishableModel, SluggedModel):
    title = models.CharField(max_length=255)
    cover_image_url = models.URLField(blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="music_release")
    streaming_links = models.JSONField(default=dict, blank=True)
    release_date = models.DateField()
    likes = models.IntegerField(default=0)

    class Meta:
        ordering = ["-release_date"]

    def __str__(self):
        return self.title

class MusicReleaseTranslation(models.Model):
    release = models.ForeignKey(MusicRelease, related_name="translations", on_delete=models.CASCADE)
    language = models.CharField(max_length=3, choices=LANGUAGES)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ("release", "language")
        verbose_name_plural = "music release translations"

    def __str__(self):
        return f"{self.release_id} [{self.language}]"


### YOUTUBE VIDEOS

def videoextras_defaults():
    return{"rating" : None}

class Video(PublishableModel):
    youtube_id = models.CharField(max_length=11, unique=True) # NOTE: Possible point of failure in the future if YouTube changes its implementation
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    internal_title = models.CharField(max_length=255)
    content_language = models.CharField(max_length=3, choices=LANGUAGES, default="fi") # NOTE: communicates what language the video itself is in ,not the metadata
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True, choices=YOUTUBE_VIDEO_CATEGORIES) #NOTE: if this needs translating, do it in frontend
    tags = models.ManyToManyField(Tag, blank=True, related_name="youtube_videos") #NOTE: if this needs translating, do it in frontend
    published_date = models.DateField()
    video_extras = models.JSONField(blank=True,default=videoextras_defaults,help_text="For example rating if the video is a review.")
    likes = models.IntegerField(default=0)

    class Meta:
        ordering = ["-published_date"]

    def __str__(self):
        return self.internal_title

class VideoTranslation(models.Model):
    youtube_video = models.ForeignKey(Video, related_name="translations", on_delete=models.CASCADE)
    language = models.CharField(max_length=3, choices=LANGUAGES)
    translated_title = models.TextField(blank=True)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ("youtube_video", "language")
        verbose_name_plural = "video translations"

    def __str__(self):
        return f"{self.youtube_video_id} [{self.language}]"


# ARTICLES EITHER HOSTED ELSEWHERE OR ON THE SITE ITSELF

def articleextras_defaults():
    return {"rating":None}

class Article(PublishableModel, SluggedModel):
    title = models.CharField(max_length=255)
    content_language = models.CharField(max_length=3, choices=LANGUAGES, default="fi")
    description = models.TextField(blank=True)
    article_image_url = models.URLField(blank=True)
    category = models.CharField(max_length=255, choices=ARTICLE_CATEGORIES)
    external_url = models.URLField(blank=True) # If the article is a link to somewhere else
    tags = models.ManyToManyField(Tag, blank=True, related_name="articles")
    published_date = models.DateField()
    article_extras = models.JSONField(default=articleextras_defaults, blank=True)
    likes = models.IntegerField(default=0)

    class Meta:
        ordering = ["-published_date"]

    def __str__(self):
        return self.title

class ArticleTranslation(models.Model):
    article = models.ForeignKey(Article, related_name="translations", on_delete=models.CASCADE)
    language = models.CharField(max_length=3, choices=LANGUAGES)
    translated_title = models.TextField(blank=True)
    description = models.TextField(blank=True)
    body_markdown = models.TextField(blank=True)

    class Meta:
        unique_together = ("article", "language")
        verbose_name_plural = "article translations"

    def __str__(self):
        return f"{self.article_id} [{self.language}]"
    

# CHANGELOG ENTRIES

class ChangelogEntry(PublishableModel):
    date = models.DateField()
    title = models.CharField(max_length=255)

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "changelog entries"

    def __str__(self):
        return f"{self.date} — {self.title}"

class ChangelogEntryTranslation(models.Model):
    changelog_entry = models.ForeignKey(ChangelogEntry, related_name="translations", on_delete=models.CASCADE)
    language = models.CharField(max_length=3, choices=LANGUAGES)
    translated_title = models.CharField(max_length=255, blank=True)
    body_markdown = models.TextField()

    class Meta:
        verbose_name_plural = "changelog entries"
        unique_together = ("changelog_entry", "language")


