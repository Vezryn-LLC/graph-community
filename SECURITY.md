# Security policy

Thank you for helping keep Graph Community secure. We welcome responsible
security research and ask that you report potential vulnerabilities privately
so they can be investigated before details are published.

## Report a vulnerability

Email **[security@vezryn.com](mailto:security@vezryn.com)** with the subject
"Graph Community security report". Reports go to a monitored Vezryn company
mailbox.

Please report potential vulnerabilities privately, such as exposed credentials,
unexpected command execution, unauthorized repository operations or bypasses of
permission boundaries. Ordinary bugs and documentation issues can use public
GitHub issues. Please allow time for investigation and remediation, and coordinate
publication of details with the maintainer.

Include the affected Graph Community version or commit/manifest digest,
operating system, Python/Codex versions, relevant file or behavior, a minimal
reproduction and expected versus observed results. Explain practical impact.
Do not include live credentials, access tokens, private repository contents or
personal data. Where necessary, arrange a safer way to share sensitive evidence.

## Operator responsibility

Graph Community is a self-hosted engineering agent orchestrator. It can execute
code and perform GitHub actions with permissions supplied by its operator. Graph
is not an authorization boundary or a security sandbox. Operators are responsible
for trusted clients, credentials, repository enrollment and the permissions
granted to agents.

For contributions touching native execution, hooks, process ownership, file
permissions or credentials, preserve conservative failure behavior. Do not
remove unknown holds, bypass ACLs or manufacture lifecycle events.
