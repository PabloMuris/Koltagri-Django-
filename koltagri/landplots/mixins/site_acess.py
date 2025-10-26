from django.shortcuts import get_object_or_404
from ..models import Site

class CurrentSiteMixin:
    def get_current_site(self):
        site_id = self.request.session.get('current_site_id')
        if not site_id:
            return None
        return get_object_or_404(Site, pk=site_id, members=self.request.user)