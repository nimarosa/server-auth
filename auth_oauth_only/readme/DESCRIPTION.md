Lets a database require an OAuth provider (for example Google) for every
internal user, while a small group keeps the password as a break-glass.

When the option is enabled:

- a password that matches for an internal user outside the group *May sign in
  with a password* is refused, on the web login form and over XML-RPC/JSON-RPC
  alike, and a warning naming the login and the channel is logged;
- API keys, OAuth tokens, passkeys, SAML and portal users keep working, and so
  does a password re-check of the user already signed in to the session (the
  identity check before creating an API key or changing the password);
- the login page shows only the OAuth provider buttons; `/web/login?password=1`
  shows the normal form;
- the public *Reset Password* form refuses internal users who must use OAuth.
  The administrator's invitation and reset buttons are not affected.

The refusal is the usual "Wrong login/password": a specific message would
confirm that the password was right.
