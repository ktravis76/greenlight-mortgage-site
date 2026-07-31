# Migration Map — kennethtravis.com → new Greenlight site

**The build rule:** this is a **recreation, not a reinvention.** The current kennethtravis.com
is the Greenlight Mortgage site. Every page, tool, and piece of content on it moves to the new
Greenlight domain — same information architecture, better execution. Kenneth knows this site.
He should recognize it, then notice everything works better.

kennethtravis.com is then emptied of mortgage content and becomes his personal site.

Source captured live Jul 28, 2026. Current site runs as **site #46 on the Loan Officer X
WordPress multisite** (theme `loparent` + child theme `custom-kenneth-travis`).

---

## Page-for-page

| # | Current URL | New page | Notes |
|---|---|---|---|
| 1 | `/` | `/` | Full homepage recreation — see breakdown below |
| 2 | `/loans/` | `/loans` | Hub page linking all six |
| 3 | `/loans/conventional-loans/` | `/loans/conventional` | Expand for SEO |
| 4 | `/loans/fha-loans/` | `/loans/fha` | Expand for SEO |
| 5 | `/loans/jumbo-loans/` | `/loans/jumbo` | **Nearly missed. It exists today.** |
| 6 | `/loans/va-loans/` | `/loans/va` | Priority — VA refi is the active revenue push |
| 7 | `/loans/usda-loans/` | `/loans/usda` | Lean into East Texas rural eligibility |
| 8 | `/loans/refinancing/` | `/loans/refinance` | Add VA IRRRL as a child page |
| 9 | `/mortgage-calculator/` | `/tools/calculator` | Rebuild properly |
| 10 | `/home-valuation-report/` | `/tools/home-value` | Rebuild properly |
| 11 | `/resources/` | `/resources` | Home buying resources |
| 12 | `/lender-learning-center/` | `/learn` | Learning Center |
| 13 | `/blog/` | `/blog` | ⚠️ Confirm where the WordPress blog physically lives before cutover |
| 14 | `/about/` | `/about` | Meet the Team |
| 15 | `/reviews/` | `/reviews` | |
| 16 | `/testimonials/` | `/testimonials` | All 7 carry over verbatim |
| 17 | `/contact/` | `/contact` | |
| 18 | `/privacy-policy/` | `/privacy` | Legal — must exist at launch |
| 19 | `/accessibility/` | `/accessibility` | Legal — must exist at launch |
| 20 | `/survey/` | `/survey` | Confirm it's still used |
| 21 | `greenlight.my1003app.com/233918/register` | **unchanged** | External LOS. Do not rebuild — see below. |

**Every one of these needs a 301 from the old URL.** That domain ranks **#2 for "mortgage
longview tx."** A missing redirect is lost equity and a dead ad destination.

---

## Homepage — what's on it today

Recreate all of it, in roughly this order:

1. **Logo + phone** `903-331-0892` in the header
2. **Nav:** Loan Options (6-item dropdown) · Resources (4-item) · Learning Center · About · Reviews · Contact
3. **Two primary CTAs:** Apply Online · Meet The Team
4. **H1:** "Longview, TX Mortgage Consultant"
5. **Four quick-access tiles:** Explore Loan Options · Mortgage Calculator · Check My Home Value · Client Testimonials
6. **Homepage video** — `kt-video.mp4`. Pull the original file before the domain flips; do not hotlink.
7. **Facebook page feed** — currently embeds `/glmtg/`
8. **Kenneth's letter** — "Dear Future Homeowner…" ⚠️ contains "I guarantee" — rephrase
9. **Core Values** — Service & Compassion · Operational Excellence · Trust & Integrity
10. **Testimonial carousel** — Tim (Longview), Jason (Gilmer), Maxwell (Jefferson), John (Longview), Robyn (Longview), Jasper (Longview), Brent (Longview)
11. **Loan officer card** — headshot, "Kenneth Travis, President-CEO NMLS# 233918", Greenlight Mortgage LLC, 4523 Judson Rd Longview TX 75605, 903-331-0892
12. **Social row** — Facebook, Instagram, LinkedIn, YouTube, Google, Zillow
13. **Compliance footer** — full text below
14. **NMLS + Equal Housing Lender badges**

---

## Compliance footer — carries over, with two fixes

Current text, verbatim:

> Greenlight Mortgage, LLC is a licensed Mortgage Broker in the state of Texas. NMLS 2426021.
> Alabama - 23417. Florida - MBR6235. Louisiana - 2426021. North Dakota - ML104832.
> South Carolina - 2426021. Texas - 2426021. This is not a commitment to lend. All loans
> subject to credit approval. Guidelines subject to change without prior notice. This
> information is provided to assist business professionals only and is not an advertisement
> extended to the consumer as defined by Section 226.2 Regulation Z.-EOE. Equal Housing Lender.
> 4523 Judson Rd Longview, TX 75605. Main: 903-331-0892.

**Fix 1 — the Reg Z line is wrong for this site.** It says the content is for *business
professionals only and not an advertisement extended to the consumer*, on a page that opens
"Dear Future Homeowner" and asks people to apply. Those contradict. Compliance resolves the
wording before it carries over.

**Fix 2 — "I guarantee"** in the welcome letter. Rephrase.

Everything else carries: six state licenses, NMLS numbers, not-a-commitment-to-lend,
credit-approval language, EHO.

---

## What we do NOT rebuild

**The loan application.** Apply Online hands off to `greenlight.my1003app.com/233918/register`
— a licensed LOS under Kenneth's own NMLS. **Keep it.** A full 1003 collects SSNs, income, and
assets — nonpublic personal information under GLBA. Rebuilding it here moves that liability
onto us for no gain.

What we add in front of it: a short pre-application intake that captures only enough to start
a conversation, then hands off clean.

---

## Where "better" actually happens

Same pages, better execution:

- **SEO.** The current title tag is `Longview Home Loans | Longview Mortgages | Home Loans in
  Longview | Longview Real Estate Mortgages` — keyword-stuffed, and Kenneth himself flagged it
  as a penalty risk on Jun 16. It is still live six weeks later because he could not change it.
  His own suggested replacement: *"Longview TX Mortgage Consultant | Greenlight Mortgage –
  Kenneth Travis."* Only ~10 pages are indexed today versus competitors with 50+.
- **Loan pages become real pages**, not stubs. This is the biggest ranking opportunity.
- **Local targeting** Kenneth asked for: Spring Hill, Pine Tree, Hallsville school districts.
- **Six-state licensing surfaced** — "We lend in 6 states" is a selling point buried in the footer.
- **Working tools**, not decorative ones — calculator, home value, Estimated Savings.
- **Forms post into Konnectd** (`LRAzmr7bQKMMlXiYfvi6`) instead of emailing a person. Today
  leads land in individual inboxes and get reconciled by hand.
- **Blog that actually publishes.** One legacy post plus 7 from July. Feed it from the
  557-video YouTube library — local content already pulls 3,000–12,000 views.
- **Speed.** Static, no WordPress, no multisite tenancy.
- **He can change it himself.**

---

## Assets to pull before the domain flips

Everything below is served from the vendor's multisite. Once the domain moves, it is gone.

- `/wp-content/themes/custom-kenneth-travis/images/kt-video.mp4` — homepage video
- `/wp-content/uploads/sites/46/2021/09/kenneth-travis-1.png` — headshot
- `/wp-content/uploads/sites/46/2023/04/greenlight-mortgage.png` — header logo
- `/wp-content/uploads/sites/46/2023/04/greenlight.png` — footer logo
- All blog post content and images
- Full testimonial text
- Any resource PDFs or downloads

**Do this first.** It is the only irreversible step in the whole project.
