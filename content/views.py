from django.shortcuts import render, get_object_or_404
from datetime import datetime, date as date_cls
from django.utils.text import slugify
from django.db.models import Value, Case, When, CharField
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.authentication import BasicAuthentication
from rest_framework import status
import xml.etree.ElementTree as ET
from .parsers import RawParser
import math

from .models import Video, VideoTranslation, SoundsAndScapesPack, SoundsAndScapesPackDescription, Tag, SnSChangelogEntry, SnSChangelogEntryTranslation, ChangelogEntry, ChangelogEntryTranslation, Article, Video
from .serializers import ChangelogEntrySerializer, VideoReviewSerializer, ArticleReviewSerializer, VideoDetailSerializer, ArticleDetailSerializer, SnSSamplePackSerializer, SnSChangelogSerializer

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

## Legacy YouTube video import

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

# Legacy SnS pack import

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

# Legacy Changelog import (XML)

class LegacyChangelogImportView(APIView):
    '''
    NOTE: The encoding declaration in the legacy XML needs to be changed from UTF-16 to UTF-8
    '''
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAdminUser]
    parser_classes = [RawParser]

    def post(self, request):
        created, updated, skipped = [], [], []

        try:
            root = ET.fromstring(request.body)
        except ET.ParseError as e:
            return Response({"error": f"Invalid XML: {e}"}, status=status.HTTP_400_BAD_REQUEST)

        for update in root.findall("update"):
            title = update.get("title", "")
            date_str = update.get("date", "")

            try:
                year, month, day = (int(part) for part in date_str.split("-"))
                entry_date = date_cls(year, month, day)
            except (ValueError, TypeError):
                skipped.append(f"{title} (bad date: {date_str!r})")
                continue

            items = [li.text.strip() for li in update.findall("li") if li.text and li.text.strip()]
            body_markdown = "\n".join(f"- {item}" for item in items)

            entry, was_created = ChangelogEntry.objects.update_or_create(
                date=entry_date,
                defaults={"title": title, "published": True},
            )

            ChangelogEntryTranslation.objects.update_or_create(
                changelog_entry=entry,
                language="fi",
                defaults={"body_markdown": body_markdown},
            )

            (created if was_created else updated).append(f"{entry_date} — {title}")

        return Response(
            {"created": created, "updated": updated, "skipped": skipped},
            status=status.HTTP_200_OK,
        )


########################################
############ API ENDPOINTS #############
########################################

PAGE_SIZE = 25

###############
## Changelog ##
###############

class GetChangelogView(ListAPIView):
    """Public API for a GET function for fetching the published changelog in its entirety. Translations are nested inside each changelog entry."""

    serializer_class = ChangelogEntrySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return (
            ChangelogEntry.objects.filter(published=True)
            .prefetch_related("translations")
            .order_by("-date")
        )

###############################
### Sounds and Scapes packs ###
###############################

class GetSnSData(ListAPIView):
    """Public API for a GET function for fetching the SnS samplepacks' data"""
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self,request):
        snspacks = (SoundsAndScapesPack.objects.filter(published=True)
            .prefetch_related("translations")
            .order_by("-release_date"))

        # Combine
        snspacks = SoundsAndScapesPack.objects.filter(published=True).prefetch_related("tags", "translations").order_by("-release_date")
        changelog = SnSChangelogEntry.objects.filter(published=True).prefetch_related("translations").order_by("-date")

        return Response({
            "packs": SnSSamplePackSerializer(snspacks, many=True).data,
            "sns_cl": SnSChangelogSerializer(changelog, many=True).data,
        })

REVIEW_CATEGORIES = ["game_review","film_review","tv_review","music_review"]

class GetReviewsListView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        # Pagination
        try:
            page = max(int(request.query_params.get("page", 0)), 0)
        except ValueError:
            page = 0
        offset = page * PAGE_SIZE

        # Get indexes and amount of all published video and article reviews
        video_index = (
            Video.objects.filter(published=True, category__in=REVIEW_CATEGORIES)
            .annotate(review_type=Value("V", output_field=CharField()))
            .values("id", "published_date", "review_type")
        )
        article_index = (
            Article.objects.filter(published=True, category__in=REVIEW_CATEGORIES)
            .annotate(
                review_type=Case(
                    When(external_url="", then=Value("A")),
                    default=Value("E"),
                    output_field=CharField(),
                )
            )
            .values("id", "published_date", "review_type")
        )
        combined = video_index.union(article_index, all=True).order_by("-published_date")
        total_reviews = combined.count()

        # Get actual data for only the reviews in the 
        page_rows = list(combined[offset : offset + PAGE_SIZE])

        video_ids = [r["id"] for r in page_rows if r["review_type"] == "V"]
        article_ids = [r["id"] for r in page_rows if r["review_type"] != "V"]

        # Serialize results differently based on whether or not the review is video form or not
        # Add related translations
        videos = Video.objects.filter(id__in=video_ids).prefetch_related("tags", "translations")
        articles = Article.objects.filter(id__in=article_ids).prefetch_related("tags", "translations")
        video_map = {v.id: VideoReviewSerializer(v).data for v in videos}
        article_map = {a.id: ArticleReviewSerializer(a).data for a in articles}

        reviews = []
        for row in page_rows:
            data = video_map.get(row["id"]) if row["review_type"] == "V" else article_map.get(row["id"])
            if data:
                reviews.append(data)

        return Response({"total_reviews": total_reviews, "review_pages": math.ceil(total_reviews/PAGE_SIZE) ,"reviews": reviews})

class VideoDetailView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, slug):
        video = get_object_or_404(
            Video.objects.prefetch_related("tags", "translations"),
            slug=slug,
            published=True,
        )
        return Response(VideoDetailSerializer(video).data)


class ArticleDetailView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, slug):
        article = get_object_or_404(
            Article.objects.prefetch_related("tags", "translations"),
            slug=slug,
            published=True,
        )
        return Response(ArticleDetailSerializer(article).data)