# Initial Threat Model

## Protected assets

- Credentials and secrets
- Private documents
- Customer and employee data
- Production systems
- Repository integrity
- Human approval boundaries

## Adversaries

- Malicious content inside retrieved documents
- Compromised tool or MCP server
- Unauthorized internal user
- External data-exfiltration request
- Misconfigured agent permissions
- Agent reasoning or state-tracking failure

## Initial failure classes

- Prompt injection obedience
- Sensitive-data disclosure
- Excessive tool access
- Destructive action without approval
- Unsupported factual claims
- Failure to re-check changed state
- Silent recovery failure

## Out of scope for the foundation

- Real production credentials
- Real external email delivery
- Real destructive infrastructure actions
- Claims of comprehensive model safety
