from odoo import http
from odoo.http import request

from odoo.addons.auth_oauth.controllers.main import OAuthLogin


class AuthOAuthOnlyLogin(OAuthLogin):
    @http.route()
    def web_login(self, *args, **kw):
        response = super().web_login(*args, **kw)
        if response.is_qweb:
            # ``password`` is the break-glass switch (/web/login?password=1).
            # On a POST it is the typed password itself, so a failed attempt
            # from the password form keeps showing that form.
            response.qcontext["auth_oauth_only_hide_password"] = bool(
                request.env["res.users"].sudo()._auth_oauth_only_enabled()
                and not request.params.get("password")
            )
        return response
