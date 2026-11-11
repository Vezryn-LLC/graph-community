# Security policy

Graph Community is a self-hosted engineering agent orchestrator. It can execute
code and perform GitHub actions with permissions supplied by its operator.
Users are responsible for trusted clients, credentials, repository enrollment
and the permissions granted to agents.

## Privately report a vulnerability

Email **[security@vezryn.com](mailto:security@vezryn.com)** with the subject
"Graph Community security report". This is Vezryn's confidential security
reporting address. It forwards to the founder's monitored company mailbox.
The founder verified an external iCloud test message, its delivery, and an
Outlook notification on November 11, 2026 (Pacific time).

Include the affected Graph Community version or commit/manifest digest,
operating system, Python/Codex versions, relevant file or behavior, a minimal
reproduction and expected versus observed results. Explain practical impact.
Do not include live credentials, access tokens, private repository contents or
personal data. Where necessary, arrange a safer way to share sensitive evidence.

**Do not report an undisclosed exploitable vulnerability through a public issue
or public pull request.** Use the email address above so the maintainer can
investigate privately. Once public GitHub private vulnerability reporting is
enabled and verified, that may become an additional channel; it is not claimed
as configured today.

No bug bounty, guaranteed response time, supported-version lifetime, security
service level or continuous maintenance commitment is promised. Reporters and
operators should not assume an immediate fix.

For contributions touching native execution, hooks, process ownership, file
permissions or credentials, preserve conservative failure behavior. Do not
remove unknown holds, bypass ACLs or manufacture lifecycle events.
