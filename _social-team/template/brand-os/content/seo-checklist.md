# SEO checklist

> Read by: content-engine. Run on every article before it leaves drafts/. Not used for social posts.
> The content engine reports each check as pass or fail in the draft's front matter.
> The first four checks are the ones the content engine agent file names. Keep them. Add your own below.

## Required checks
| # | Check | Pass when |
|---|---|---|
| S1 | Keyword in the title | The primary keyword from the brief appears in the title |
| S2 | Keyword early | The primary keyword appears in the first 100 words |
| S3 | Keyword in a heading | The primary keyword, or a close form of it, appears in at least one H2 |
| S4 | Meta description | Written, 155 characters or fewer, and it says what the reader gets |
| S5 | One owner | No other page in signals-seo/keyword-map.md owns this keyword |
| S6 | One H1 | The page has exactly one H1 |
| S7 | Internal links | Links to [FILL IN: how many] related pages listed in keyword-map.md |
| S8 | Image alt text | Every image has alt text that describes it |
| S9 | Slug | Short, lower case, words joined with hyphens, contains the keyword |
| S10 | Facts | Every number has a source in the brief or messaging-bank.md, or is marked [VERIFY] |

## Your own checks
| # | Check | Pass when |
|---|---|---|
| S11 | [FILL IN: e.g. Surfer content score] | [FILL IN: the score you accept] |
| S12 | [FILL IN] | [FILL IN] |

## How a fail is handled
- S1 to S9: the content engine fixes it and runs the check again.
- S10: it never invents a source. It leaves [VERIFY] in place and lists it for you.

## Example report (Northwind Coffee)
seo_check: S1 pass, S2 pass, S3 pass, S4 pass, S5 pass, S6 pass, S7 pass, S8 fail (one image without alt text, fixed), S9 pass, S10 pass
