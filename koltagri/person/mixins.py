import uuid



from django.utils.translation import gettext_lazy as _




import koltagri.core.constants as core_constants





class ModelRolesMixin:

    @property
    def is_site_owner(self):
        return self.group.name == core_constants.ROLE_SITE_OWNER
    
    @property
    def is_site_manager(self):
        return self.group.name == core_constants.ROLE_SITE_MANAGER

    @property
    def is_site_team(self):
        return self.group.name == core_constants.ROLE_SITE_TEAM

    @property
    def is_site_member(self):
        return (
            self.group.name == core_constants.ROLE_SITE_TEAM
            or self.group.name == core_constants.ROLE_SITE_MANAGER
            or self.group.name == core_constants.ROLE_SITE_OWNER
        )
    

   