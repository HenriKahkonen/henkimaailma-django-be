from django.db import models
from django.utils.text import slugify

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



# ///////////////////////////////
# /// Constant specifications ///
# ///////////////////////////////

LANGUAGES = [
    ("fi", "Finnish"),
    ("en", "English"),
]

ARTICLE_CATEGORIES = [
    ("blog", "blog post"), 
    ("game_review","game review"),
    ("music_review","music review"), 
    ("film_review","film review"), 
    ("tv_review","tv review"), 
    ("project_writeup","project writeup"),
]

YOUTUBE_VIDEO_CATEGORIES = [
    ("game_review","game review"),
    ("video_essay","video essay"),
    ("vlog","vlog"),
    ("commentary","commentary"),
]

# ///////////////////////////////////////
# ///// Actually usable data models /////
# ///////////////////////////////////////


### SNS SAMPLE PACKS

class SoundsAndScapesPack(PublishableModel,SluggedModel):
    title = models.CharField(max_length=255)
    cover_image_url = models.URLField(blank=True)
    external_url = models.URLField()
    file_list = models.JSONField(default=dict, blank=True)
    release_date = models.DateField()
    likes = models.IntegerField(default=0)

    class Meta:
        ordering = ["-release_date"]
        verbose_name_plural = "Sounds and Scapes -sample packs"

    def __str__(self):
        return self.title

class SoundsAndScapesPackTranslation(models.Model):
    snspack = models.ForeignKey(SoundsAndScapesPack, related_name="translations", on_delete=models.CASCADE)
    language = models.CharField(max_length=3, choices=LANGUAGES)
    description = models.TextField(blank=True)
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags")

    class Meta:
        unique_together = ("snspack","language")
        verbose_name_plural = "Sounds and Scapes -sample pack translations"


    def __str__(self):
        return f"{self.snspack_id} [{self.language}]"


### MUSIC RELEASES

class MusicRelease(PublishableModel, SluggedModel):
    title = models.CharField(max_length=255)
    cover_image_url = models.URLField(blank=True)
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
    tags = models.CharField(max_length=255,blank=True,help_text="Comma-separated tags (genres and the like)")
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ("release", "language")
        verbose_name_plural = "music release translations"

    def __str__(self):
        return f"{self.release_id} [{self.language}]"


### YOUTUBE VIDEOS

class Video(PublishableModel):
    youtube_id = models.CharField(max_length=11, unique=True) # NOTE: Possible point of failure in the future if YouTube changes its implementation
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=100, blank=True, choices=YOUTUBE_VIDEO_CATEGORIES) # NOTE: if this needs to be translated, do it in frontend
    video_language = models.CharField(max_length=3, choices=LANGUAGES) # NOTE: communicates what language the video itself is in ,not the metadata
    published_date = models.DateField()
    likes = models.IntegerField(default=0)

    class Meta:
        ordering = ["-published_date"]

    def __str__(self):
        return self.title

class VideoTranslation(models.Model):
    youtube_video = models.ForeignKey(Video, related_name="translations", on_delete=models.CASCADE)
    language = models.CharField(max_length=3, choices=LANGUAGES)
    translated_title = models.TextField(blank=True)
    tags = models.CharField(max_length=255,blank=True,help_text="Tags for the video")
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ("youtube_video", "language")
        verbose_name_plural = "video translations"

    def __str__(self):
        return f"{self.youtube_video_id} [{self.language}]"


# ARTICLES EITHER HOSTED ELSEWHERE OR ON THE SITE ITSELF

class Article(PublishableModel, SluggedModel):
    title = models.CharField(max_length=255)
    article_image_url = models.URLField(blank=True)
    article_category = models.CharField(choices=ARTICLE_CATEGORIES)
    external_url = models.URLField(blank=True) # If the article is a link to somewhere else
    published_date = models.DateField()
    likes = models.IntegerField(default=0)

    class Meta:
        ordering = ["-published_date"]

    def __str__(self):
        return self.title


class ArticleTranslation(models.Model):
    article = models.ForeignKey(Article, related_name="translations", on_delete=models.CASCADE)
    language = models.CharField(max_length=3, choices=LANGUAGES)
    summary = models.TextField()
    body_markdown = models.TextField()

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
    changelogEntry = models.ForeignKey(ChangelogEntry, related_name="translations", on_delete=models.CASCADE)
    language = models.CharField(max_length=3, choices=LANGUAGES)
    body_markdown = models.TextField()
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated")

    class Meta:
        verbose_name_plural = "changelog entries"
        unique_together = ("changelogEntry", "language")


