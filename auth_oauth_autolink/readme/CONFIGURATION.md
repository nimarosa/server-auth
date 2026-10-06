1. Activate the developer mode.
2. Go to **Settings > Users & Companies > OAuth Providers** and open the
   provider you want to link accounts through.
3. Tick **Auto-link existing users by email**.

The flag is per provider and off by default. Enable it only for a provider you
trust to verify e-mail ownership, because that claim is the whole trust anchor
of this module.

Administrators (members of **Administration / Settings**) are never linked
automatically. Link them by hand: open the user, go to the **Oauth** tab and
set **OAuth Provider** and **OAuth User ID** to the identifier the provider
reports for that account (`sub` for OpenID Connect providers).
