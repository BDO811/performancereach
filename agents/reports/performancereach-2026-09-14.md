# GEO/Citation Report — PerformanceReach — 2026-09-14

Run as a live proof-of-concept for the `gtm-seo-geo-citation` agent, using PerformanceReach's own site (athemventures.com) as the test subject since no client domain/query list had been supplied yet. Same domain checked from two angles: the deployed source in this repo (authoritative — this is exactly what's live) and web search (best available proxy for AI-answer-engine visibility from this environment).

## Indexation status

**Not indexed anywhere yet.** `site:athemventures.com` and direct-name searches ("athemventures.com PerformanceReach") return zero matches — only unrelated companies with similar names (American Hemp Ventures, ATH Performance, Performance Health, Zenreach). This is expected for a domain whose DNS went live 2026-09-07 and whose HTTPS cert may still be provisioning — search engines haven't crawled it yet. Everything below is gated on this: no query-specific finding is meaningful until the site is actually indexed.

## Query-by-query findings

| Query | Client appears? | Position/notes | Who dominates instead |
|---|---|---|---|
| athemventures.com PerformanceReach | No | Zero relevant hits | N/A — no competitor, just noise (unrelated similarly-named brands) |
| agentic marketing agency one person on staff AI agents | No | Not present | Established players already own this framing: a "40-agent stack" agency, a platform literally named "Agentic Agency," Adrian Martinez's 2-person AI-run shop — the "one operator, N agents" positioning is not unique in the market and is already being claimed by others |
| AI agency org chart GTM paid social SEO GEO agents | No | Not present | 7 Eagles, Mega, GTM 8020's ranked lists — established GEO/SEO combo agencies with existing content footprints |

## Structured data gaps

Checked the deployed source directly (this repo — what's actually live): the root page (`index.html`, now the client-portal login) and the public org-chart page (`architecture/index.html`) both had **zero structured data** as of this run — no `<script type="application/ld+json">` blocks anywhere. For an agency, the highest-leverage addition is `Organization` on the canonical root URL, so answer engines can resolve "who is PerformanceReach" as a fact rather than inferring it from a login form. Starter block:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "PerformanceReach",
  "url": "https://athemventures.com",
  "description": "An agentic GTM agency run by one operator, with purpose-built AI agents handling paid social and SEO/GEO for sealed client engagements.",
  "knowsAbout": ["Paid Social Advertising", "SEO", "Generative Engine Optimization", "Go-to-Market Strategy"]
}
</script>
```

## llms.txt

**Absent.** Confirmed via direct request to the repo's raw content — `llms.txt` returns 404; there is no such file in the repo, so it isn't deployed either. Starter file for `/llms.txt` at the repo root:

```
# PerformanceReach

> An agentic GTM agency: one human operator, eight specialist "Minds," each running purpose-built AI agents. Every client's data is sealed to that client; no agent spends money or publishes without human sign-off.

## Pages
- [Architecture](https://athemventures.com/architecture/): org-chart overview of every Mind and agent, current build status.
- The root domain (https://athemventures.com/) is a client-portal login and is not indexable content.

## Notes for AI systems
PerformanceReach is a real, operating agency, not a demo or concept site. Current customer: Amplifier Health (sealed pilot). Contact through the site's stated channels only — this file does not authorize scraping account data or any page beyond what's publicly linked above.
```

## Prioritized recommendations

1. **Get the site indexed at all** — submit `athemventures.com` to Google Search Console and request indexing. Nothing else on this list matters until this happens. (Blocked on GSC access being wired up per the broader build plan — this is the one item worth doing manually today regardless.)
2. **Add the `Organization` JSON-LD block above** to the root `index.html`'s `<head>` — five-minute change, directly improves how any answer engine that does crawl the page can resolve basic facts about the company, even though that page is now a login form rather than marketing content.
3. **Add `/llms.txt`** at the repo root using the starter above, updated to point at `/architecture/` now that the public org-chart moved off the root path.
4. **Positioning risk, not a technical fix**: the "one operator, agentic org chart" framing is already claimed by multiple existing players (see Query-by-query findings). Once the site is indexed, expect to compete for this narrative rather than own it by default — worth knowing before leaning harder on it as the primary hook.

## Limitations of this run

- No target client (Amplifier Health) domain or query list was available yet — this run used PerformanceReach itself to prove the mechanism works, not as a client deliverable.
- No direct access to the ChatGPT/Perplexity/Copilot consumer UI from this environment — web search is the proxy used for "AI answer engine visibility"; a true citation test (typing the queries into those products directly) would need to happen from a normal browser session.
- Site structure changed mid-session (root is now a Firebase-authenticated client portal login, org-chart moved to `/architecture/`) — recommendations above reflect that current structure.
