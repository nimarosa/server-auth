from lxml import html

from odoo.tests import HttpCase, tagged

from .common import ENABLED_PARAM


def has_class(css_class):
    """XPath predicate for an HTML class (lxml has no ``hasclass``)."""
    return f"contains(concat(' ', @class, ' '), ' {css_class} ')"


@tagged("post_install", "-at_install")
class TestLoginPage(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.ref("auth_oauth.provider_google").write(
            {"enabled": True, "client_id": "oauth-only-test.apps.example.com"}
        )
        cls.env["ir.config_parameter"].sudo().set_param(
            "auth_signup.reset_password", "True"
        )

    def _page(self, url="/web/login"):
        response = self.url_open(url)
        self.assertEqual(response.status_code, 200)
        return html.fromstring(response.content)

    def _assert_password_form(self, page, shown):
        checks = {
            "login input": page.xpath("//form//input[@name='login']"),
            "password input": page.xpath("//form//input[@name='password']"),
            "submit button": page.xpath("//form//button[@type='submit']"),
            "reset password link": page.xpath(
                "//a[contains(@href, '/web/reset_password')]"
            ),
        }
        for what, nodes in checks.items():
            if shown:
                self.assertTrue(nodes, f"{what} missing")
            else:
                self.assertFalse(nodes, f"{what} should be hidden")
        # The provider buttons are there either way.
        self.assertTrue(page.xpath(f"//div[{has_class('o_auth_oauth_providers')}]//a"))

    def test_switch_off_shows_password_form(self):
        self._assert_password_form(self._page(), shown=True)

    def test_switch_on_shows_only_providers(self):
        self.env["ir.config_parameter"].sudo().set_param(ENABLED_PARAM, "True")
        page = self._page()
        self._assert_password_form(page, shown=False)
        # The form must not stay hidden waiting for the user switcher.
        form = page.xpath(f"//form[{has_class('oe_login_form')}]")[0]
        self.assertNotIn("d-none", form.get("class").split())
        self.assertFalse(page.xpath("//owl-component[@name='web.user_switch']"))
        # No dangling "- or -" separator above the providers.
        self.assertFalse(page.xpath("//em[normalize-space()='- or -']"))

    def test_switch_on_break_glass_url_shows_password_form(self):
        self.env["ir.config_parameter"].sudo().set_param(ENABLED_PARAM, "True")
        self._assert_password_form(self._page("/web/login?password=1"), shown=True)
