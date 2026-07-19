# Erga MCP router installed

This opt-in Hermes plugin treats a recognized job link as an explicit request to create local
Erga MCP review artifacts. It never submits an application or contacts an employer.
The separate user-invoked monitor command may schedule private alerts back to its origin chat.

Hermes Agent 0.18.2 or newer is required for the `pre_llm_call` context hook and stable
`ctx.dispatch_tool(name, args)` interface used by this plugin. Run `hermes --version` to check and
`hermes update` before enabling the plugin if needed.

Register the MCP server with the standard `erga-mcp` or `erga_mcp` name before
enabling this plugin. Both names produce the default Hermes tool name
`mcp__erga_mcp__intake_job_url`.

If you deliberately used another MCP server name, set `ERGA_MCP_TOOL` in the Hermes
process environment to its complete prefixed intake-tool name. Restart the gateway after changing
plugin state or environment variables.

At gateway startup, MCP discovery can finish just after the first user message. The router retries
only Hermes' exact `Unknown tool` and `MCP server ... is not connected` readiness errors for up to
30 seconds. Set `ERGA_MCP_READY_TIMEOUT_SECONDS` to a value from 0 through 30 to
change that bounded wait; 0 disables retries. The retry interval defaults to 0.25 seconds and can
be adjusted, up to 5 seconds, with `ERGA_MCP_READY_RETRY_SECONDS`. Operational
intake failures are returned immediately and are never retried.

“Summarize only” and “don't run the pipeline” opt out. A request such as “don't just
summarize—run the pipeline” still runs intake, as requested.

When intake returns a successfully validated PDF, gateway-delivered replies (Discord, Signal,
Telegram, and similar message platforms) include it as a native document attachment. The plugin
unwraps Hermes' MCP result envelope, validates that the file is a real PDF inside the returned
package's `artifacts` directory, and adds Hermes' outbound document-upload directive. A server-local
path is never presented as a substitute for the upload. Local CLI responses remain text-only.

After official-posting intake, the router also uses the host's generic `web_search` tool for one
Reddit/community query and one broader company/role query, then records the bounded results through
`record_secondary_research`. The output is stored separately from official facts and labeled as
unverified. Set `ERGA_MCP_WEB_SEARCH_TOOL` only if the host uses a different generic tool
name; if search is unavailable, primary intake and the PDF attachment still proceed.

To enable the monitoring half, first configure `mail` in the local pipeline config, then run
`/setup-erga-monitor` in the private connected conversation that should receive alerts. The
plugin prepares two no-agent scripts and creates an every-15-minute event monitor plus a daily
history digest. Hermes captures the current chat/thread as the delivery origin. The event monitor
stays silent when no new relevant messages are found. The command works even when the connected
platform does not expose the general `cronjob` toolset, and installs runners in the active Hermes
profile. `/setup-erga-monitor 14` uses a 14-day window for the daily digest.

Run `/export-erga` to create a private ZIP containing application records, recruiting-event
and audit history, evidence, and generated job packages. The plugin validates that the ZIP is
inside the configured export directory and sends it as a native document attachment rather than a
server-local path.
