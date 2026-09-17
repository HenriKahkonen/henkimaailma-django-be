from analytics.models import ViewCount, ViewEvent
from django.contrib import admin

@admin.register(ViewCount)
class ViewCountAdmin(admin.ModelAdmin):
    list_display = ("content_type_label","slug","count")
    list_filter = ("content_type",)
    search_fields = ('object_id',)
    ordering = ('-count'),

    @admin.display(description='Content type', ordering='content_type')
    def content_type_label(self,obj):
        return obj.content_type.model_class().__name__

    @admin.display(description='Slug')
    def slug(self,obj):
        target = obj.content_object
        return target.slug if target else '(deleted)'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('content_type').prefetch_related('content_object')

@admin.register(ViewEvent)
class ViewEventAdmin(admin.ModelAdmin):
    list_display = ("content_type_label","slug","created_at","visitor_hash")
    list_filter = ("content_type",)
    search_fields = ("object_id","visitor_hash")
    ordering = ('-created_at',)

    @admin.display(description='Content type', ordering='content_type')
    def content_type_label(self,obj):
        return obj.content_type.model_class().__name__

    @admin.display(description='Slug')
    def slug(self,obj):
        target = obj.content_object
        return target.slug if target else '(deleted)'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('content_type').prefetch_related('content_object')
