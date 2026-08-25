from django.shortcuts import render
from datetime import datetime
from django.utils.text import slugify
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import BasicAuthentication
from rest_framework import status

from .models import Video, VideoTranslation, Tag

####################################
## Reusable funcs 
####################################

def get_or_create_tag(name):
    tag = Tag.objects.filter(name__iexact=name).first()
    if tag:
        return tag
    return Tag.objects.create(name=name, slug=slugify(name))

########################################
######### LEGACY IMPORT VIEWS ##########
########################################
###### Comment these out after the #####
##### operation has been completed #####
########################################


CATEGORY_MAPPING_YOUTUBE = {
        "peliarviot" : "game_review",
        "euroviisut" : "commentary",
        "muu video" : "video_essay",
        "vlogit" : "vlog",
    }

class LegacyVideoImportView(APIView):
    """
    One-shot bulk import from the old JSON structure.
    POST body: the full legacy JSON object, e.g. {"peliarviot": [...], "vlogit": [...]}
    """
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request):
        payload = request.data
        created, updated, skipped = [], [], []

        for category_key, entries in payload.items():

            mapped_category = CATEGORY_MAPPING_YOUTUBE.get(category_key)
            if mapped_category is None:
                skipped.extend(
                    f"{category_key}:{entry.get('id', 'unknown')}" for entry in entries
                )
                continue
            
            for entry in entries:
                ytid = entry.get("ytid")
                if not ytid:
                    skipped.append(entry.get("id", "unknown"))
                    continue

                date_str = entry.get("date")
                published_date = (
                    datetime.fromisoformat(date_str.replace("Z", "+00:00")).date()
                    if date_str else None
                )

                video, was_created = Video.objects.update_or_create(
                    youtube_id=ytid,
                    defaults={
                        "internal_title": entry.get("title", ""),
                        "slug": entry.get("url", ""),
                        "category": mapped_category,
                        "published_date": published_date,
                        "video_language": "fi",
                        "published": True,
                    },
                )

                VideoTranslation.objects.update_or_create(
                    youtube_video=video,
                    language="fi",
                    defaults={
                        "translated_title": entry.get("title",""),
                        "description": entry.get("desc",""),
                    },
                )
                
                tag_objs = [get_or_create_tag(name) for name in entry.get("tags", [])]
                video.tags.set(tag_objs)

                (created if was_created else updated).append(ytid)

        return Response(
            {"created": created, "updated": updated, "skipped": skipped},
            status=status.HTTP_200_OK,
        )