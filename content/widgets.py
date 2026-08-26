# content/widgets.py
from django.utils.text import slugify
from django_select2.forms import ModelSelect2TagWidget
from .models import Tag

class TagWidget(ModelSelect2TagWidget):
    model = Tag
    search_fields = ["name__icontains"]
    queryset = Tag.objects.all()

    def value_from_datadict(self, data, files, name):
        """Any typed value that isn't an existing Tag PK gets created as a new Tag."""
        values = set(super().value_from_datadict(data, files, name))
        cleaned = []
        for value in values:
            if value.isdigit() and Tag.objects.filter(pk=value).exists():
                cleaned.append(value)
            else:
                tag, _ = Tag.objects.get_or_create(
                    name=value, defaults={"slug": slugify(value)}
                )
                cleaned.append(str(tag.pk))
        return cleaned