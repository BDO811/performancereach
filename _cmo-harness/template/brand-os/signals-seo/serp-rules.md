# SERP rules

> Read by: search-visibility, market-radar, and the playbooks ranking-drops-a-page and search-demand-spikes.
> These rules decide which search changes are worth acting on. Anything under these lines is noise:
> it goes in the weekly summary and nothing else happens.
> Every number below is yours to set. Until you set it, agents report the change and take no action.

## 1. A ranking drop
- Counts when a page falls [FILL IN: how many positions a page can drop before it counts] positions for its primary keyword in keyword-map.md
- Compared with: [FILL IN: last week, or the average of a period you choose]
- Ignore keywords with fewer than [FILL IN: monthly searches below which you do not care] monthly searches
- Ignore pages that are not in keyword-map.md: [FILL IN: yes or no]
- What happens: search-visibility checks the page and the results page, then the orchestrator runs /ranking-drops-a-page

## 2. A demand spike
- Counts when impressions or searches for a query rise by [FILL IN: the rise that counts as a spike] over [FILL IN: the period you compare against]
- Read from: [FILL IN: the Google Search Console impressions export, the Semrush export, or both]
- Only for queries that: [FILL IN: match a cluster in keyword-map.md, or any query]
- What happens: the orchestrator runs /search-demand-spikes

## 3. A competitor move on the results page
- Counts when a competitor from brand-brain/positioning.md enters the top [FILL IN: how many results you watch] for one of your primary keywords
- What happens: market-radar adds it to its weekly report. No content is written unless the orchestrator briefs it.

## 4. Results page features we care about
| Feature | Do we want it | Which pages |
|---|---|---|
| Featured snippet | [FILL IN: yes or no] | [FILL IN] |
| People also ask | [FILL IN] | [FILL IN] |
| Local pack (map results) | [FILL IN] | [FILL IN] |
| Video results | [FILL IN] | [FILL IN] |
| Image results | [FILL IN] | [FILL IN] |

## 5. How loud each change is
| Level | Example | Who hears about it | When |
|---|---|---|---|
| Low | [FILL IN: a small move on a minor keyword] | weekly summary only | weekly |
| Medium | [FILL IN] | the orchestrator briefs a department | next run |
| High | [FILL IN: a top page drops out of view] | an alert to the owner | [FILL IN: right away, or next morning] |

Example row (Northwind Coffee): | High | The pour over guide stops showing for "how to brew pour over coffee" | alert to the owner | next morning |

## 6. Never
- Change a live page without the change passing owner/approval-bar.md.
- Act on one day of data.
