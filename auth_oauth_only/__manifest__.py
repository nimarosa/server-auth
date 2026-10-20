# Copyright 2026 Nimarosa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "OAuth Only Login for Internal Users",
    "summary": "Internal users sign in only through OAuth; a group keeps the "
    "password as a break-glass",
    "version": "18.0.1.0.0",
    "category": "Authentication",
    "website": "https://github.com/OCA/server-auth",
    "author": "Nimarosa, Odoo Community Association (OCA)",
    "maintainers": ["nimarosa"],
    "license": "AGPL-3",
    "development_status": "Beta",
    "depends": [
        "auth_oauth",
    ],
    "data": [
        "security/res_groups.xml",
        "views/res_config_settings_views.xml",
        "views/auth_oauth_only_templates.xml",
    ],
    "installable": True,
}
