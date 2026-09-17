from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType

###############################
## View tracking serializers ##
###############################

class TrackViewSerializer(serializers.Serializer):
    model = serializers.CharField(max_length=100)
    slug = serializers.SlugField()

    def validate(self, data):
        try:
            content_type = ContentType.objects.get(
                app_label='content', model=data['model']
            )
        except ContentType.DoesNotExist:
            raise serializers.ValidationError({'model': 'Unknown content type.'})

        model_class = content_type.model_class()

        try:
            # Don't let calls increment count of unpublished objects
            obj = model_class.objects.get(slug=data['slug'], published=True)
        except model_class.DoesNotExist:
            raise serializers.ValidationError({'slug':'Object not found'})
        
        data['content_type'] = content_type
        data['object_id'] = obj.pk

        return data