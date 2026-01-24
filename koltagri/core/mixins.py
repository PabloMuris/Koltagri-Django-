from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from koltagri.core.constants import (
    ROLE_EMPLOYEE,
    ROLE_TECNICAL_ASSISTANCE,
    ROLE_SITE_MANAGER
)
from koltagri.landplots.models import SiteMembership


class SiteRequiredMixin(LoginRequiredMixin):
    """
    Mixin para garantir que um site foi selecionado na sessão.
    Redireciona para a página de seleção de site se não houver site selecionado.
    """
    
    def dispatch(self, request, *args, **kwargs):
        # Verifica se há um site selecionado na sessão
        if not request.session.get('selected_site_location'):
            return redirect('select_site')
        return super().dispatch(request, *args, **kwargs)


class IsInGroupPassesTestMixin(SiteRequiredMixin, UserPassesTestMixin):
    """
    Mixin base para verificar se o usuário pertence a um site
    com um ou mais papéis permitidos.
    Herda de SiteRequiredMixin para garantir que há um site selecionado.
    """
    required_roles = None  # agora no plural

    def get_site_id(self):
        """
        Centraliza a lógica de onde o site_id pode vir.
        """
        return self.request.session.get("selected_site_location")

    def test_func(self):
        site_id = self.get_site_id()

        if not self.required_roles or not site_id:
            return False

        # garante que sempre será uma lista/tupla
        roles = self.required_roles
        if not isinstance(roles, (list, tuple, set)):
            roles = [roles]

        return SiteMembership.objects.filter(
            user=self.request.user,
            site_id=site_id,
            role__name__in=roles
        ).exists()

    def handle_no_permission(self):
        """
        Redireciona para a página de seleção de site se o usuário
        não tiver um site selecionado ou não tiver permissão.
        """
        site_id = self.get_site_id()
        if not site_id:
            return redirect('select_site')
        # Se tiver site mas não tiver permissão, retorna o comportamento padrão (403)
        return super().handle_no_permission()


class IsManagerMixin(IsInGroupPassesTestMixin):
    required_roles = ROLE_SITE_MANAGER


class IsManagerOrTechnicalAssistanceMixin(IsInGroupPassesTestMixin):
    required_roles = [
        ROLE_SITE_MANAGER,
        ROLE_TECNICAL_ASSISTANCE
    ]


class IsStaffMixin(IsInGroupPassesTestMixin):
    required_roles = (
        ROLE_EMPLOYEE,
        ROLE_SITE_MANAGER,
        ROLE_TECNICAL_ASSISTANCE
    )