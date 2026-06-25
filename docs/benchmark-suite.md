# Vigilattice Adversarial Benchmark Suite

Vigilattice evaluates autonomous agents against reproducible safety scenarios rather
than judging only the final natural-language response.

## Built-in controls

| Benchmark | Risk | Safety control |
|---|---|---|
| VL-PI-001 | Prompt injection | Separate trusted instructions from retrieved content |
| VL-DLP-001 | Secret exfiltration | Prevent sensitive-data disclosure and transmission |
| VL-HIL-001 | Approval bypass | Require human authorization before dangerous actions |
| VL-AUTH-001 | Cross-tenant access | Enforce tenant and resource boundaries |
| VL-TOOL-001 | Destructive tool use | Prevent irreversible execution without safeguards |
| VL-SE-001 | Social engineering | Verify identity and reject procedural bypass attempts |

Each evaluation captures structured events, accessed resources, security decisions,
approval ordering, policy findings, evidence, remediation guidance, and separate
task-performance and safety scores.

The `mock-safe` and `mock-unsafe` adapters are deterministic reference implementations.
They provide stable regression baselines before evaluating non-deterministic LLM agents.
