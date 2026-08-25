from django.shortcuts import render
from datetime import datetime
from django.utils.text import slugify
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import BasicAuthentication
from rest_framework import status

from .models import Video, VideoTranslation, SoundsAndScapesPack, SoundsAndScapesPackDescription, Tag, SnSChangelogEntry, SnSChangelogEntryTranslation

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
###### Feel free to ####################
###### comment these out after the #####
##### operation has been completed #####
########################################

CATEGORY_MAPPING_YOUTUBE = {
        "peliarviot" : "game_review",
        "euroviisut" : "commentary",
        "muu video" : "video_essay",
        "vlogit" : "vlog",
    }

class LegacyVideoImportView(APIView):

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


LICENCE_MAPPING = {
    "CC0" : "cc0"
}

class LegacySnSPackImportView(APIView):

    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request):
        payload = request.data
        created, updated, skipped = [], [], []

        for category_key, entries in payload.items():

            for entry in entries:

                if category_key == "Changelog":
                    date_str = entry.get("Date")
                    published_date = (
                        datetime.fromisoformat(date_str.replace("Z", "+00:00")).date()
                        if date_str else None
                    )
                    contents_array = entry.get("Contents")
                    contents_markdown_string = ""
                    for item in contents_array:
                        contents_markdown_string += f"- {item} \n"

                    # old data didn't have titles for sns changelog
                    new_title = published_date

                    changelogentry, was_created = SnSChangelogEntry.objects.update_or_create(
                        date = published_date,
                        defaults={
                            "title": new_title,
                        },
                    )

                    SnSChangelogEntryTranslation.objects.update_or_create(
                        changelog_entry = changelogentry,
                        language = "en",
                        defaults = {
                            "body_markdown" : contents_markdown_string,
                        }
                    )

                    (created if was_created else updated).append(new_title)

                elif category_key == "Packs":

                    date_str = entry.get("Date")
                    published_date = (
                        datetime.fromisoformat(date_str.replace("Z", "+00:00")).date()
                        if date_str else None
                    )

                    updated_str = entry.get("UpDated")
                    updated_date = (
                        datetime.fromisoformat(updated_str.replace("Z", "+00:00")).date()
                        if updated_str else published_date
                    )

                    samplepack, was_created = SoundsAndScapesPack.objects.update_or_create(
                        title = entry.get("Name",""),
                        defaults={
                            "cover_image_url": entry.get("Img", ""),
                            "external_url": entry.get("DownloadLink",""),
                            "release_date": published_date,
                            "updated_date": updated_date,
                            "licence": LICENCE_MAPPING.get(entry.get("Licence"), "all_rights_reserved"), # all imported legacy packs have cc0
                            "file_list": entry.get("FileListing", []),

                            "published": True,
                        }
                    )

                    SoundsAndScapesPackDescription.objects.update_or_create(
                        snspack=samplepack,
                        language="en",
                        defaults={
                            "description": entry.get("Desc",""),
                        },
                    )

                    (created if was_created else updated).append(entry.get("Name"))

        return Response(
            {"created": created, "updated": updated, "skipped": skipped},
            status=status.HTTP_200_OK,
        )