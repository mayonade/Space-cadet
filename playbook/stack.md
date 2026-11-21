# Tool stack

What does the actual sending. The director updates the Status column as things get connected.
Tool names are suggestions; any equivalent works.

| Job | Options | Status |
|---|---|---|
| Lead system of record | Zoho CRM | Connected, but read permission denied - needs fixing |
| Booking | Calendly | Connected |
| Glue between tools | Zapier | Connected |
| Email sequences at volume | Zoho Campaigns / CRM cadences, or a dedicated sequencer | Not chosen |
| One-to-one email drafts | Gmail | Connected (drafts and replies, not bulk) |
| LinkedIn | Manual send from a daily queue; Sales Navigator helps | Manual |
| Retargeting ads | Meta, LinkedIn Matched Audiences, Google Customer Match | No ad accounts connected |
| Site tracking | Meta Pixel, LinkedIn Insight Tag, Google tag on the landing page | Unknown |
| Postcards and letters | A print-and-mail API (Lob, PostGrid, Postalytics) | Not chosen |
| Handwritten notes | A handwriting service (e.g. Handwrytten) | Not chosen |
| Information kits | Local printer or fulfillment house | Not chosen |
| Landing page + personal URLs / QR | Whatever hosts the site, with UTM-tagged links | Unknown |

## Notes

- **Sending domain.** Do bulk email from a separate domain or subdomain, warmed up over a few
  weeks, so a deliverability problem cannot hurt the main inbox.
- **Audience minimums.** Ad platforms need a minimum number of matched people before a list
  audience will serve (hundreds for LinkedIn and Meta, more for Google). Small segments get
  pooled.
- **Attribution.** Every channel links to the same landing page with its own UTM tags, and every
  mail piece carries its own QR code, so a booked call can be traced to the touches before it.
  The CRM gets a "last touch" and "all touches" field per lead.
- **Mail triggers.** Zapier can watch for a click or booking-page view and place the mail order
  automatically, once a mail vendor is chosen and the owner has approved the standing rule.
