- The rule lives in `res.users._check_credentials` and treats the
  `auth_method` values `password` and `ldap` as a password. It sees the final
  result of every override loaded before it (`auth_ldap`, `auth_passkey`,
  `auth_saml`, `auth_oauth_multi_token`, `auth_admin_passkey`); a module that
  depends on this one and catches `AccessDenied` to re-authenticate the same
  password would bypass it.
- Emptying the break-glass group while the option is on is not prevented.
- Portal users keep their password, but the login page hides the form for
  them too: they need `/web/login?password=1`.
