MAX_CHAR_FIELD_NAME_LENGTH = 255
MEDIUM_CHAR_FIELD_NAME_LENGTH = 100
SMALL_CHAR_FIELD_NAME_LENGTH = 50
PUBLIC_STRING = "PUBLIC"
PRIVATE_STRING = "PRIVATE"

# Definição de constantes para os papéis

ROLE_SYSTEM_ADMIN   = "System Admin"    # Admin geral do sistema
ROLE_SITE_OWNER     = "Site Owner"      # Criador/administrador de um site específico
ROLE_SITE_MANAGER        = "Site Manager"         # Sócio/gerente do site (perms ≅ Site Owner)
ROLE_SITE_TEAM       = "Sitr Team"        # Funcionário (perms restritas)
ROLE_STUDY_TEAM     = "Study Team"      
ROLE_STUDY_MANAGER  = "Study Manager" # Especialista/agrônomo do estudo


SITE_MANAGEMENT_ROLES = [
    ROLE_SITE_OWNER,
    ROLE_SITE_MANAGER,
]

# Quem pertence ao grupo de execução de estudos
STUDY_EXECUTION_ROLES = [
    ROLE_STUDY_TEAM,
    ROLE_STUDY_MANAGER,
]

# Todos os papéis disponíveis no sistema
ALL_ROLES = [
    ROLE_SYSTEM_ADMIN,
    *SITE_MANAGEMENT_ROLES,
    ROLE_SITE_TEAM,
    *STUDY_EXECUTION_ROLES,
]

ROLE_MANAGEMENT_HIERARCHY = {

    ROLE_SITE_OWNER: [
        ROLE_SITE_OWNER,
        *SITE_MANAGEMENT_ROLES,   # inclui Partner
        ROLE_SITE_TEAM,
        *STUDY_EXECUTION_ROLES,
    ],

    ROLE_SITE_MANAGER: [
        ROLE_SITE_TEAM,
        *STUDY_EXECUTION_ROLES,
    ],
    ROLE_STUDY_MANAGER: [
        ROLE_STUDY_TEAM,
    ]
}
