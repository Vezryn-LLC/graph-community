# Native model and reasoning selection

Codex chooses the model and reasoning effort; Python resolves guidance and wakes
the coordinator. A model name, subscription, worker count or entitlement is not
bundled with Graph Community. Keep the user's configured model when capable.

Check `codex --version` and `codex exec --help` on the actual installation.
Help documents supported configuration options, not account access or subagent
overrides. Inspect the native client's available model/profile interface when
exposed. If no catalog is available, inherit the configured default rather than
guessing identifiers. Use only options that the installed client actually supports.

Match actual task complexity, uncertainty, correctness risk and cost. Begin with
the lightest demonstrated-capable configuration; increase effort for observed
need. Documentation usually needs less reasoning than difficult concurrency or
authorization debugging. Priority describes urgency, not reasoning difficulty.
No family ranking, mandatory reviewer profile or benchmark claim is implied.

When native worker overrides are supported, request the selected available model
and effort at dispatch. Otherwise inherit the coordinator configuration and note
any material substitution in the claim. On an unsupported configuration error,
retry with a known available configuration after checking whether allocation
occurred. Distinguish provider/quota interruption from implementation failure;
preserve existing worker ownership and source rather than duplicate assignments.

Use [ROUTING_MATRIX.md](ROUTING_MATRIX.md) as examples, not an enforced router.
Never build a model gateway, proxy, custom scheduler or entitlement bypass to
obtain a preferred route. Do not spend inference on repeated unchanged polling.
