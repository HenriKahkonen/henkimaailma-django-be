from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType

########################################
## View and like tracking serializers ##
########################################

def find_slugged_object(data):
    """
    Helper function that checks data['model'] and data['slug'] and returns the content_type and object of the correct slugged object. Throws Validationerror if model or slug is not found.
    """
    try:
        content_type = ContentType.objects.get(
            app_label='content', model=data['model']
        )
    except ContentType.DoesNotExist:
        raise serializers.ValidationError({'model': 'Unknown content type.'})

    model_class = content_type.model_class()

    try:
        # published=True <-- Only return objects that have been published
        obj = model_class.objects.get(slug=data['slug'], published=True)

    except model_class.DoesNotExist:
        raise serializers.ValidationError({'slug':'Object not found'})

    return content_type, obj

    
class TrackViewSerializer(serializers.Serializer):
    model = serializers.CharField(max_length=100)
    slug = serializers.SlugField()

    def validate(self, data):

        content_type, obj = find_slugged_object(data)
        
        data['content_type'] = content_type
        data['object_id'] = obj.pk

        return data

class LikeToggleSerializer(serializers.Serializer):
    model = serializers.CharField(max_length=100)
    slug = serializers.SlugField()

    def validate(self, data):

        content_type, obj = find_slugged_object(data)

        data['content_type'] = content_type
        data['object_id'] = obj.pk
        data['obj'] = obj  # the actual instance, needed to update `likes` directly

        return data