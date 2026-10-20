from odoo.tests.common import TransactionCase, new_test_user

ENABLED_PARAM = "auth_oauth_only.enabled"
INTERNAL_PASSWORD = "internal-Pa55word!"
PORTAL_PASSWORD = "portal-Pa55word!"
BREAK_GLASS_PASSWORD = "break-glass-Pa55word!"


class AuthOAuthOnlyCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = cls.env.ref("auth_oauth_only.group_password_login")
        cls.internal = new_test_user(
            cls.env,
            login="oauth_only_internal",
            password=INTERNAL_PASSWORD,
            email="internal@example.com",
            groups="base.group_user",
        )
        cls.portal = new_test_user(
            cls.env,
            login="oauth_only_portal",
            password=PORTAL_PASSWORD,
            email="portal@example.com",
            groups="base.group_portal",
        )
        cls.break_glass = new_test_user(
            cls.env,
            login="oauth_only_break_glass",
            password=BREAK_GLASS_PASSWORD,
            email="break-glass@example.com",
            groups="base.group_user,auth_oauth_only.group_password_login",
        )

    def _set_enabled(self, value):
        self.env["ir.config_parameter"].sudo().set_param(ENABLED_PARAM, value)

    def _check(self, user, password, interactive=True):
        credential = {"login": user.login, "password": password, "type": "password"}
        return (
            self.env["res.users"]
            .with_user(user)
            ._check_credentials(credential, {"interactive": interactive})
        )
