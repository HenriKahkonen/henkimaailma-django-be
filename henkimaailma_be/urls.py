"""
URL configuration for henkimaailma_be project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from content.views import LegacyVideoImportView, LegacySnSPackImportView, GetChangelogView, GetReviewsListView, VideoDetailView, ArticleDetailView, GetSnSData
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('select2/', include('django_select2.urls')),
    # Public get
    path("get-changelog/", GetChangelogView.as_view(), name="changelog-list"),
    path("get-sns-data/", GetSnSData.as_view(), name="sns-packs-list"),
    path("get-reviews-list/", GetReviewsListView.as_view(), name="reviews-list"),
    path("videos/<slug:slug>/", VideoDetailView.as_view()),
    path("articles/<slug:slug>/", ArticleDetailView.as_view()),
]

if settings.DEBUG:

    try:
        from content.views import LegacyVideoImportView
        urlpatterns += [
            path('import/legacy-videos/', LegacyVideoImportView.as_view()),
        ]
    except ImportError:
        pass

    try:
        from content.views import LegacySnSPackImportView
        urlpatterns += [
            path('import/legacy-sns-packs/', LegacySnSPackImportView.as_view()),
        ]
    except ImportError:
        pass

    try:
        from content.views import LegacyChangelogImportView
        urlpatterns += [
            path('import/legacy-changelog/', LegacyChangelogImportView.as_view())
        ]
    except ImportError:
        pass

    try:
        from content.views import BackupExportView, BackupRestoreView
        urlpatterns += [
            path('backup/export', BackupExportView.as_view(), name="backup-export"),
            path('backup/restore', BackupRestoreView.as_view(), name="backup-restore")
        ]
    except ImportError:
        pass
