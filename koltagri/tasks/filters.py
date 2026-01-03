import django_filters
from .models import Attachment

class AttachmentFilter(django_filters.FilterSet):
    class Meta:
        model = Attachment
        fields = ["name"]