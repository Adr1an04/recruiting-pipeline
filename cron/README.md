# Hermes Recruiting Monitor

The monitor uses two deterministic `--no-agent` jobs. They never submit applications, reply to
mail, or invoke an LLM:

- `erga-mail-monitor` runs every 15 minutes. It reads bounded Inbox metadata, records each
  provider message ID once, and delivers only newly detected assessments, interviews, offers,
  acknowledgements, decisions, and recruiter leads. Empty output is silent.
- `erga-history-digest` runs daily at 9:00. It reports application-status counts and recent
  recruiting-event history so the user gets a regular pipeline overview.

## Recommended setup from a connected conversation

First configure the selected provider. For Zoho, the client ID is non-secret and belongs in the
local config; the client secret and tokens remain in the operating-system credential store:

```bash
uv run erga mail configure \
  --config /absolute/path/to/config.toml \
  --provider zoho \
  --client-id '<client-id>'
```

After enabling the MCP server and Hermes router plugin, run this slash command in the private
Discord, Telegram, Signal, or other connected conversation that should receive alerts:

```text
/setup-erga-monitor
```

The command installs the runners under `$HERMES_HOME/scripts/` (or `~/.hermes/scripts/` when
`HERMES_HOME` is unset), creates both cron jobs without an LLM, and omits an explicit delivery
override so Hermes captures the current chat and thread as the delivery origin. Repeating the
command refreshes the scripts and does not duplicate jobs with the same names. An optional integer
changes the history window:

```text
/setup-erga-monitor 14
```

## CLI preparation and explicit targets

The same scripts can be prepared without the plugin:

```bash
uv run erga monitor install-hermes-scripts \
  --config /absolute/path/to/config.toml
```

Then create jobs with an explicit private destination. `origin` only resolves to a messaging chat
when creation occurs inside that chat; a local shell should use a concrete target such as
`discord:<chat-id>` or `telegram:<chat-id>:<thread-id>`.

```bash
hermes cron create '*/15 * * * *' \
  --name erga-mail-monitor \
  --script erga-mcp-mail.py \
  --no-agent \
  --deliver 'discord:<chat-id>'

hermes cron create '0 9 * * *' \
  --name erga-history-digest \
  --script erga-mcp-history.py \
  --no-agent \
  --deliver 'discord:<chat-id>'
```

Hermes requires cron scripts to live under its active `$HERMES_HOME/scripts/` and does not pass
prompt text as script arguments in `--no-agent` mode. The generated runners therefore use a
private, non-secret sidecar containing only the local config path, history window, package path,
and pipeline Python executable.

Review the delivery target before enabling a job: subjects and sender addresses are private
metadata. Message previews are used transiently for classification but are not retained or sent.
