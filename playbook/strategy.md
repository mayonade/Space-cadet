# Strategy

## The one metric

**Intro calls booked per 1,000 leads contacted, and cost per booked call.** Measured against the
10% holdout, so we count calls outreach caused, not calls that would have happened anyway.

Downstream, tracked in the CRM and reviewed monthly: call show rate, candidates who reach a
franchise shortlist, franchisor introductions, signed agreements. A tactic that books many calls
with people who never show is a losing tactic.

Leading indicators (reply rate, click rate, connection accept rate) are used to call tests
faster. They are never the goal.

## Who buys

Most leads are browsing. Buyers tend to show some of these:

- A trigger: layoff or buyout, burnout in a corporate role, a liquidity event, kids leaving home.
- Means: roughly $100k+ liquid or a path to it (retirement rollover, SBA loan, home equity).
- A timeframe they can name.
- Behavior: they reply, click, come back to the site, or look at the booking page.

Behavior beats stated answers. A lead who said "$500k, ready now" and ignores everything ranks
below one who said nothing and clicked twice.

## Tiers and the spend ladder

`tools/mkt.py ingest` scores every lead on fit, recency and engagement. The weights are a
starting guess; the analyst recalibrates them against who actually books.

| Tier | Who | Channels | Rough spend per lead |
|---|---|---|---|
| C | Old, thin, unengaged | Email nurture, ad audience | cents |
| B | Decent fit or recent | + LinkedIn, heavier ad frequency, a postcard on engagement | $1-3 |
| A | Strong fit or engaged | + handwritten note, phone, information kit once they respond | $8-15, kit $25-40 |

Dollar figures are planning estimates; replace them with real vendor quotes in `stack.md`.

Leads move up the moment they act. A Tier C lead who clicks is Tier A that day.

## The orchestrated sequence (Tier A, 21 days)

The point of omni-channel is that each touch makes the next one familiar. Same face, same
promise, same landing page across all of them.

| Day | Touch |
|---|---|
| 0 | Email 1: short, plain text, one question. Lead joins ad audiences. |
| 1 | LinkedIn: connection request, no pitch. |
| 3 | Email 2: the lead magnet (fit quiz or buyer's guide). |
| 5 | Mail: handwritten note with a QR code to a personal page. |
| 7 | LinkedIn: message after they accept; otherwise skip. |
| 10 | Email 3: a candidate story (no earnings figures). |
| 12 | Phone call and voicemail. Text only with written consent on file. |
| 14 | Mail: information kit, only to leads who have engaged. |
| 17 | Email 4: handle the main objection (money, risk, time). |
| 21 | Email 5: close the loop. Then monthly nurture. |

Ads run underneath the whole time: the lead sees the same name and offer in their feed between
touches.

**Triggers override the calendar:**

- Clicks any link: call task within the hour during business hours.
- Views the booking page without booking: next-day email and a postcard.
- Replies: the sequence stops and a human takes over.
- Books: all outreach stops; confirmation and pre-call sequence begin.
- Opts out anywhere: removed everywhere.

Tier B gets days 0, 1, 3, 10, 21 plus ads. Tier C gets a monthly email and ads.

## How we test

- One variable per test. Random assignment by `mkt.py assign`, never by hand.
- Sample size computed before launch. Booked calls are rare, so most tests are called on a
  leading indicator and then confirmed on booked calls over a longer window.
- Each test is written up in `experiments/` before it runs: hypothesis, metric, size, stop date.
- Winners become the new control. Every result, including flat ones, goes in `learnings.md`.
- Order of testing: offer and angle first (largest effect), then channel mix and sequence
  order, then timing, then wording. Subject-line polishing comes last.
