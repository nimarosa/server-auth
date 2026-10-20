from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import ENABLED_PARAM, AuthOAuthOnlyCase


@tagged("post_install", "-at_install")
class TestSettings(AuthOAuthOnlyCase):
    def _param(self):
        return self.env["ir.config_parameter"].sudo().get_param(ENABLED_PARAM)

    def _save(self, enabled):
        settings = self.env["res.config.settings"].create(
            {"auth_oauth_only_enabled": enabled}
        )
        settings.execute()

    def test_off_by_default(self):
        self.assertFalse(self._param())
        self.assertFalse(
            self.env["res.config.settings"].create({}).auth_oauth_only_enabled
        )

    def test_enable_with_a_break_glass_user(self):
        self._save(True)
        self.assertEqual(self._param(), "True")
        self.assertTrue(
            self.env["res.config.settings"].create({}).auth_oauth_only_enabled
        )

    def test_refuse_to_enable_without_break_glass_user(self):
        self.group.sudo().write({"users": [(5, 0, 0)]})
        with self.assertRaises(UserError):
            self._save(True)
        self.assertFalse(self._param())

    def test_inactive_members_do_not_count(self):
        self.group.sudo().write({"users": [(5, 0, 0)]})
        self.break_glass.active = False
        self.group.sudo().write({"users": [(4, self.break_glass.id)]})
        with self.assertRaises(UserError):
            self._save(True)

    def test_disable_always_works(self):
        self._set_enabled("True")
        self.group.sudo().write({"users": [(5, 0, 0)]})
        self._save(False)
        self.assertFalse(self._param())

    def test_resave_when_already_enabled_does_not_block_other_settings(self):
        """The guard is about the transition off -> on; once the switch is on,
        saving unrelated settings must not start failing."""
        self._set_enabled("True")
        self.group.sudo().write({"users": [(5, 0, 0)]})
        self._save(True)
        self.assertEqual(self._param(), "True")
