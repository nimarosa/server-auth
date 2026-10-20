from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import AuthOAuthOnlyCase


@tagged("post_install", "-at_install")
class TestResetPassword(AuthOAuthOnlyCase):
    """The self-service "reset password" form calls ``res.users.reset_password``."""

    def _reset(self, login):
        return self.env["res.users"].sudo().reset_password(login)

    def test_switch_off_internal_may_reset(self):
        self._reset(self.internal.login)
        self.assertEqual(self.internal.partner_id.signup_type, "reset")

    def test_switch_on_internal_without_group_refused(self):
        self._set_enabled("True")
        with self.assertRaises(UserError):
            self._reset(self.internal.login)
        self.assertNotEqual(self.internal.partner_id.signup_type, "reset")

    def test_switch_on_refused_by_email_too(self):
        self._set_enabled("True")
        with self.assertRaises(UserError):
            self._reset(self.internal.email)

    def test_switch_on_break_glass_may_reset(self):
        self._set_enabled("True")
        self._reset(self.break_glass.login)
        self.assertEqual(self.break_glass.partner_id.signup_type, "reset")

    def test_switch_on_portal_may_reset(self):
        self._set_enabled("True")
        self._reset(self.portal.login)
        self.assertEqual(self.portal.partner_id.signup_type, "reset")

    def test_switch_on_admin_invitation_still_works(self):
        """The admin-side buttons (invite, send reset instructions) are not the
        self-service form: inviting a new internal user must keep working, the
        user then accepts the invitation with Google."""
        self._set_enabled("True")
        self.internal.with_context(create_user=1).action_reset_password()
        self.assertEqual(self.internal.partner_id.signup_type, "signup")
