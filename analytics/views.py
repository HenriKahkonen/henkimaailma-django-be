from datetime import timedelta
from django.db import models as db_models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status, throttling
import hashlib
from django.utils import timezone

from analytics.models import ViewEvent, ViewCount
from analytics.serializers import TrackViewSerializer

##############################
## Count unique page visits ##
##############################

# How long until the same IP address can view the same object to count as new page view
DEDUP_WINDOW = timedelta(hours=3)

class ViewTrackThrottle(throttling.AnonRateThrottle):
    scope = 'view_track'

class TrackViewAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ViewTrackThrottle]

    def post(self, request):
        serializer = TrackViewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        content_type = serializer.validated_data['content_type']
        object_id = serializer.validated_data['object_id']

        # Anonymize the user ip - server doesn't need to know who accessed page but it needs to know has the same person accessed it recently
        ip = request.META.get('REMOTE_ADDR', '')
        ua = request.META.get('HTTP_USER_AGENT', '')
        visitor_hash = hashlib.sha256(
            f"{ip}{ua}{timezone.now().date()}".encode()
        ).hexdigest()

        recent_exists = ViewEvent.objects.filter(
            content_type=content_type,
            object_id=object_id,
            visitor_hash=visitor_hash,
            created_at__gte=timezone.now() - DEDUP_WINDOW,
        ).exists()

        counted = False
        if not recent_exists:
            ViewEvent.objects.create(
                content_type=content_type,
                object_id=object_id,
                visitor_hash=visitor_hash,
                object_slug=serializer.validated_data['slug']
            )
            ViewCount.objects.get_or_create(
                content_type=content_type, object_id=object_id
            )
            ViewCount.objects.filter(
                content_type=content_type, object_id=object_id
            ).update(count=db_models.F('count') + 1)
            counted = True

        return Response({'status': 'ok', 'counted': counted}, status=status.HTTP_200_OK)
