# greenlight-mortgage-site

Consumer marketing site for **Greenlight Mortgage**, powered by Co/LAB Lending. Longview, TX.

- **Vercel project:** `greenlight-mortgage-site`
- **Preview:** https://greenlight-mortgage-site.vercel.app
- **Domain:** not yet assigned — pending KT decision
- **Supabase:** project `athovwknbwbbqworsbrm` (Greenlight Mortgage, us-east-2)

## Do not confuse with `greenlight-mortgage`

The Vercel project named `greenlight-mortgage` is the **internal Sales Dashboard**
(VA IRRRL pipeline, speed-to-lead, leaderboard, live Teli data). It is not a website.
Do not deploy over it.

## Compliance — required on every consumer-facing page

- "Powered by Co/LAB Lending"
- Company NMLS # and branch NMLS #
- Individual NMLS # on every loan officer bio
- Equal Housing Opportunity
- "This is not a commitment to lend"
- "Subject to credit approval and underwriting" on anything showing a number
- Texas Department of Savings and Mortgage Lending license disclosure
- No stated rates, APRs, payments, or approval guarantees
- Rate quotes and eligibility deferred to licensed loan officers

Any tool that outputs dollar figures (savings estimator, cheat sheet) needs
estimate-only framing and compliance sign-off before it ships.

## Migration source

Replaces the mortgage content currently on kennethtravis.com, which runs as
site #46 on the Loan Officer X WordPress multisite. Cutover requires a full
301 redirect map — that domain ranks #2 for "mortgage longview tx".

Loan pages to carry over: Conventional, FHA, **Jumbo**, VA, USDA, Refinancing.

## Stack

Static HTML/CSS. No build step, no dependencies. Deploys on push.
