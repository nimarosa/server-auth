1. Make sure the OAuth provider works for your users.
2. Move integrations that log in over RPC with a password to an API key.
3. Add yourself, and whoever else needs a break-glass, to the group
   *May sign in with a password* (category *Extra Rights*). Nobody gets it on
   install.
4. In *Settings > General Settings > Integrations*, tick *Sign in only with
   OAuth*. Odoo refuses to save it while the group has no active internal
   member.

The option is the system parameter `auth_oauth_only.enabled`; setting it to
`False` (or unticking the option) turns the module off at once.
