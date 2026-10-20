import logging

from odoo import _, api, models
from odoo.exceptions import AccessDenied, UserError
from odoo.http import request
from odoo.tools import str2bool

_logger = logging.getLogger(__name__)

ENABLED_PARAM = "auth_oauth_only.enabled"
PASSWORD_LOGIN_GROUP = "auth_oauth_only.group_password_login"
# auth_method values that mean "a password typed by the user matched":
# ``password`` from base (and from auth_admin_passkey's master password) and
# ``ldap`` from auth_ldap, which checks the same form field against LDAP.
PASSWORD_AUTH_METHODS = frozenset({"password", "ldap"})


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _auth_oauth_only_enabled(self):
        value = self.env["ir.config_parameter"].sudo().get_param(ENABLED_PARAM)
        try:
            return str2bool(value or "False")
        except ValueError:
            return False

    def _auth_oauth_only_must_use_oauth(self):
        """Whether this user may not sign in with a password."""
        self.ensure_one()
        return bool(
            not self.share
            and self._auth_oauth_only_enabled()
            and not self.has_group(PASSWORD_LOGIN_GROUP)
        )

    def _auth_oauth_only_refuses(self, auth_info):
        """Whether ``auth_info`` is a password sign-in this database forbids.

        ``self.env.user`` is the user being authenticated, as in
        ``_check_credentials``.
        """
        return bool(
            auth_info.get("auth_method") in PASSWORD_AUTH_METHODS
            and self.env.user._auth_oauth_only_must_use_oauth()
        )

    def _auth_oauth_only_is_identity_check(self):
        """A password re-check of the user already signed in to this session.

        That is Odoo's "sudo mode" (identity check before creating an API key,
        changing the password, enabling 2FA...), not a sign-in: the session was
        opened by an allowed method, so the password grants nothing new.
        """
        return bool(request and request.session.uid == self.env.uid)

    def _check_credentials(self, credential, env):
        auth_info = super()._check_credentials(credential, env)
        if (
            self._auth_oauth_only_refuses(auth_info)
            and not self._auth_oauth_only_is_identity_check()
        ):
            _logger.warning(
                "Password sign-in refused for internal user %s (#%s) over %s: "
                "this database only allows OAuth (%s). An integration should "
                "use an API key instead of the password.",
                self.env.user.login,
                self.env.uid,
                "an interactive sign-in"
                if (env or {}).get("interactive", True)
                else "RPC (non-interactive)",
                ENABLED_PARAM,
            )
            raise AccessDenied()
        return auth_info

    @api.model
    def reset_password(self, login):
        """Refuse the self-service reset for users who must use OAuth.

        Only the public "Reset Password" form calls this method; the
        administrator's buttons (invitation, reset instructions) call
        ``action_reset_password`` and are not affected.
        """
        users = self.search(self._get_login_domain(login))
        if not users:
            users = self.search(self._get_email_domain(login))
        if len(users) == 1 and users._auth_oauth_only_must_use_oauth():
            raise UserError(
                _(
                    "This account signs in with an OAuth provider only: use the "
                    "provider button on the login page."
                )
            )
        return super().reset_password(login)
