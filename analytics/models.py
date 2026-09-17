from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

### Site traffic counting models

class ViewEvent(models.Model):
    '''
    Raw event of a site visitor clicking open a page or an article.
    '''
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    object_slug = models.SlugField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    visitor_hash = models.CharField(max_length=64, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['content_type', 'object_id', 'created_at']),
        ]

class ViewCount(models.Model):
    '''
    Actual viewcount of different objects.
    '''
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type','object_id')
    count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('content_type', 'object_id')