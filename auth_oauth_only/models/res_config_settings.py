from odoo import _, fields, models
from odoo.exceptions import UserError

from .res_users import ENABLED_PARAM, PASSWORD_LOGIN_GROUP


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    auth_oauth_only_enabled = fields.Boolean(
        string="Sign in only with OAuth",
        config_parameter=ENABLED_PARAM,
        help="Internal users may only sign in through an OAuth provider. Members "
        'of the "May sign in with a password" group keep their password, and '
        "/web/login?password=1 shows them the password form.",
    )

    def set_values(self):
        if self.auth_oauth_only_enabled and not (
            self.env["res.users"]._auth_oauth_only_enabled()
        ):
            self._auth_oauth_only_check_break_glass()
        return super().set_values()

    def _auth_oauth_only_check_break_glass(self):
        group = self.env.ref(PASSWORD_LOGIN_GROUP)
        members = group.sudo().users.filtered(lambda u: u.active and not u.share)
        if not members:
            raise UserError(
                _(
                    "Nobody would be left able to sign in with a password. Add "
                    'at least one active internal user to the group "%(group)s" '
                    "before enabling this option.",
                    group=group.name,
                )
            )
