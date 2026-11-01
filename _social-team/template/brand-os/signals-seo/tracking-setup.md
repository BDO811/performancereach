# Tracking setup

> Read by: search-visibility, market-radar. The orchestrator reads it to know which data is fresh.
> One row per signal: where it comes from, how it gets into this folder, and how often.
> Start every row with a manual export. Switch a row to an API or MCP connection later; nothing else changes.

## Feeds
| Signal | Tool | How it gets in | File name | How often | Who drops it | Used by |
|---|---|---|---|---|---|---|
| Search queries, clicks, positions | Google Search Console | export | gsc-queries-YYYY-MM-DD.csv | [FILL IN] | [FILL IN] | search-visibility |
| Sessions and where they came from | Google Analytics 4 | export | ga4-sessions-YYYY-MM-DD.csv | [FILL IN] | [FILL IN] | search-visibility, results-roi |
| Rankings, yours and competitors' | Semrush | export | semrush-rankings-YYYY-MM-DD.csv | [FILL IN] | [FILL IN] | search-visibility, market-radar |
| Backlinks | Ahrefs | export | ahrefs-backlinks-YYYY-MM-DD.csv | [FILL IN] | [FILL IN] | search-visibility |
| Site crawl issues | Screaming Frog | export | crawl-YYYY-MM-DD.csv | [FILL IN] | [FILL IN] | search-visibility |
| Reviews | Google Business Profile | export | gbp-reviews-YYYY-MM-DD.csv | [FILL IN] | [FILL IN] | reviews-reputation (through the orchestrator) |
| Facebook and Instagram insights | Meta Business Suite | export | meta-insights-YYYY-MM-DD.csv | [FILL IN] | [FILL IN] | publishing-social, results-roi |
| Company page analytics | LinkedIn | export | linkedin-page-YYYY-MM-DD.csv | [FILL IN] | [FILL IN] | publishing-social, results-roi |
| Channel analytics | YouTube | export | youtube-YYYY-MM-DD.csv | [FILL IN] | [FILL IN] | creative-studio, results-roi |
| Web mentions | Brand24 | export | brand24-mentions-YYYY-MM-DD.csv | [FILL IN] | [FILL IN] | market-radar, reviews-reputation |
| Audience research | SparkToro | export | sparktoro-YYYY-MM-DD.csv | [FILL IN] | [FILL IN] | market-radar |
| Competitor traffic | Similarweb | export | similarweb-YYYY-MM-DD.csv | [FILL IN] | [FILL IN] | market-radar |
| Alerts | Google Alerts | email digest saved as text | google-alerts-YYYY-MM-DD.md | [FILL IN] | [FILL IN] | market-radar |

Delete the rows for tools you do not use. Add a row for any tool you do.

## Freshness
- A file counts as stale when it is older than [FILL IN: how old an export can be before agents stop trusting it]
- A stale file is reported, never acted on: the agent writes "data stale" in its report and takes no action on that signal.

## Moving a row to a connection
| Tool | Connected through | Switched on | Notes |
|---|---|---|---|
| [FILL IN] | [FILL IN: API or MCP server name] | [FILL IN: date] | [FILL IN] |

## Never
- Paste an API key, password or token into this folder. Connections hold their own keys.
