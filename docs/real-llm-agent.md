# Real structured LLM agent

Vigilattice includes an OpenAI-compatible adapter named `llm-structured`.

The adapter sends each benchmark scenario to a configured language model and
requires a strict JSON action plan. The resulting actions are converted into the
same `AgentTrace` structure used by deterministic reference agents.

## Security boundary

The adapter operates in sandbox mode:

- Generated tool calls are recorded but not executed.
- No production credentials are exposed to the model.
- Dangerous actions remain visible to the evaluation engine.
- Sensitive-data and approval flags are captured in every generated event.
- Provider timeouts, HTTP failures, malformed responses, and schema violations
  fail safely.

## Configuration

Copy `.env.example` to `.env` and configure:

- `VIGILATTICE_LLM_API_KEY`
- `VIGILATTICE_LLM_BASE_URL`
- `VIGILATTICE_LLM_MODEL`

The default configuration targets an OpenAI-compatible Groq endpoint using a
structured-output-capable model.
