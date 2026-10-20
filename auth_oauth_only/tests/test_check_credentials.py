from unittest import mock

from odoo.exceptions import AccessDenied
from odoo.tests import tagged

from ..models import res_users as res_users_module
from .common import (
    BREAK_GLASS_PASSWORD,
    INTERNAL_PASSWORD,
    PORTAL_PASSWORD,
    AuthOAuthOnlyCase,
)


@tagged("post_install", "-at_install")
class TestCheckCredentials(AuthOAuthOnlyCase):
    def test_switch_off_password_works(self):
        for interactive in (True, False):
            info = self._check(self.internal, INTERNAL_PASSWORD, interactive)
            self.assertEqual(info["auth_method"], "password")
            self.assertEqual(info["uid"], self.internal.id)

    def test_missing_or_garbage_param_means_off(self):
        self.env["ir.config_parameter"].sudo().search(
            [("key", "=", "auth_oauth_only.enabled")]
        ).unlink()
        self.assertEqual(
            self._check(self.internal, INTERNAL_PASSWORD)["auth_method"], "password"
        )
        self._set_enabled("not-a-boolean")
        self.assertEqual(
            self._check(self.internal, INTERNAL_PASSWORD)["auth_method"], "password"
        )

    def test_switch_on_internal_password_rejected_interactive(self):
        self._set_enabled("True")
        with self.assertLogs(res_users_module.__name__, "WARNING"):
            with self.assertRaises(AccessDenied):
                self._check(self.internal, INTERNAL_PASSWORD, interactive=True)

    def test_switch_on_internal_password_rejected_rpc(self):
        self._set_enabled("True")
        with self.assertLogs(res_users_module.__name__, "WARNING") as logs:
            with self.assertRaises(AccessDenied):
                self._check(self.internal, INTERNAL_PASSWORD, interactive=False)
        # An integration still on a password must be obvious from the log.
        self.assertIn(self.internal.login, logs.output[0])
        self.assertIn("RPC", logs.output[0])

    def test_switch_on_wrong_password_still_plain_access_denied(self):
        self._set_enabled("True")
        with self.assertRaises(AccessDenied):
            self._check(self.internal, "wrong")

    def test_switch_on_break_glass_group_may_use_password(self):
        self._set_enabled("True")
        for interactive in (True, False):
            info = self._check(self.break_glass, BREAK_GLASS_PASSWORD, interactive)
            self.assertEqual(info["auth_method"], "password")

    def test_switch_on_portal_password_works(self):
        self._set_enabled("True")
        for interactive in (True, False):
            info = self._check(self.portal, PORTAL_PASSWORD, interactive)
            self.assertEqual(info["auth_method"], "password")

    def test_switch_on_api_key_works(self):
        key = (
            self.env["res.users.apikeys"]
            .with_user(self.internal)
            .sudo()
            ._generate(None, "oauth-only test", None)
        )
        self._set_enabled("True")
        info = self._check(self.internal, key, interactive=False)
        self.assertEqual(info["auth_method"], "apikey")

    def test_switch_on_oauth_token_works(self):
        provider = self.env.ref("auth_oauth.provider_google")
        self.internal.sudo().write(
            {
                "oauth_provider_id": provider.id,
                "oauth_uid": "google-uid-1",
                "oauth_access_token": "oauth-token-1",
            }
        )
        self._set_enabled("True")
        credential = {
            "login": self.internal.login,
            "token": "oauth-token-1",
            "type": "oauth_token",
        }
        # Interactive only: /auth_oauth/signin is the one caller, and base's
        # non-interactive API-key fallback reads credential["password"].
        info = (
            self.env["res.users"]
            .with_user(self.internal)
            ._check_credentials(credential, {"interactive": True})
        )
        self.assertEqual(info["auth_method"], "oauth")

    def test_ldap_counts_as_a_password(self):
        """auth_ldap returns 'ldap' for a password typed into the same form."""
        users = self.env["res.users"].with_user(self.internal)
        self._set_enabled("True")
        self.assertTrue(users._auth_oauth_only_refuses({"auth_method": "ldap"}))
        self.assertTrue(users._auth_oauth_only_refuses({"auth_method": "password"}))
        for method in ("apikey", "oauth", "passkey", "saml"):
            self.assertFalse(users._auth_oauth_only_refuses({"auth_method": method}))

    def test_identity_check_inside_own_session_is_allowed(self):
        """Re-checking the password of the user already signed in (sudo mode)
        is not a sign-in: it must keep working, e.g. to create an API key."""
        self._set_enabled("True")
        fake_request = mock.MagicMock()
        fake_request.session.uid = self.internal.id
        with mock.patch.object(res_users_module, "request", fake_request):
            info = self._check(self.internal, INTERNAL_PASSWORD)
        self.assertEqual(info["auth_method"], "password")

    def test_session_of_another_user_does_not_exempt(self):
        self._set_enabled("True")
        fake_request = mock.MagicMock()
        fake_request.session.uid = self.break_glass.id
        with mock.patch.object(res_users_module, "request", fake_request):
            with self.assertRaises(AccessDenied):
                self._check(self.internal, INTERNAL_PASSWORD)

    def test_anonymous_session_does_not_exempt(self):
        self._set_enabled("True")
        fake_request = mock.MagicMock()
        fake_request.session.uid = None
        with mock.patch.object(res_users_module, "request", fake_request):
            with self.assertRaises(AccessDenied):
                self._check(self.internal, INTERNAL_PASSWORD)
