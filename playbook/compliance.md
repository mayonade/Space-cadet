# Compliance rules

The `compliance-reviewer` enforces this file. It is a working checklist, not legal advice. Have a
franchise attorney review it once, and again before any new channel or state-specific campaign.

## Franchise-specific

- **No earnings claims.** No statement or implication of sales, income, profit, ROI, payback
  period, or "replace your salary", in copy, images, testimonials or ad targeting text. Financial
  performance information comes only from a franchisor's disclosure document, presented by the
  franchisor.
- No guarantees of success, approval, funding or territory availability.
- Testimonials must be real, attributable, and free of earnings figures.
- Do not name or use the marks of a franchise brand in ads or mail without that brand's
  permission. Several states regulate advertising of specific franchise offerings; generic
  consulting marketing is lower risk, brand-specific marketing needs attorney sign-off.
- Say plainly what the consultant is and how they are paid if the copy mentions cost
  ("free to you" is fine when true; say the franchisor pays the fee if asked).
- Funding language (retirement rollovers, SBA loans) is educational only. No tax or
  investment advice; refer to qualified providers.

## Email (US: CAN-SPAM, plus mailbox provider rules)

- True sender name, truthful subject line, a working unsubscribe, a physical postal address.
- Honor opt-outs within 10 business days; we do it immediately and across all channels.
- Bulk sending needs SPF, DKIM and DMARC on the sending domain, one-click unsubscribe, and a
  spam complaint rate kept well under 0.3%.
- Leads outside the US (Canada, UK, EU) have stricter consent rules. Exclude them until reviewed.

## Phone and text (TCPA)

- Marketing texts and autodialed or prerecorded calls need prior express written consent.
  No consent on file, no text. `mkt.py export` only lists leads with `sms_consent`.
- Scrub manual call lists against the National Do Not Call Registry unless the lead inquired
  within the last 3 months or has an existing relationship. Keep an internal do-not-call list.
- Calling hours: 8am to 9pm in the lead's time zone. Some states are stricter.

## LinkedIn

- Automated sending and scraping break LinkedIn's terms and can get the account restricted.
  The team drafts and queues; a human sends, within conservative daily limits.
- Keep it personal and one-to-one. No mass-identical messages.

## Ads

- Customer-list audiences require that we have the right to use the data and that opt-outs are
  removed. Refresh audiences whenever the suppression list changes.
- Ad copy must not assert personal attributes ("Laid off?", "Are you 50 and stuck?"). Speak to
  interests, not to the reader's circumstances.
- Platforms may classify business-opportunity ads into restricted categories with limited
  targeting. Check current policy at launch; do not work around a classification.
- Landing pages need a privacy policy that discloses tracking pixels and ad retargeting.

## Direct mail

- Honor do-not-mail requests. Use a real return address.
- Same content rules as everywhere else: no earnings claims, nothing styled to look like a
  government notice, invoice or check.

## Data

- Lead data stays in `data/` and the CRM. Never in git, never in prompts to outside services
  beyond the vendor doing that channel's delivery.
- Only use data the lead gave us or that is ordinary business contact data. No appending of
  sensitive attributes (health, finances beyond what they stated, family status).
