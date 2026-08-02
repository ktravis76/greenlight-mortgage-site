# Handoff — get the site live

Everything is built, committed and verified. Three things need a human with
credentials. Paste the block below into Claude Code / Cowork.

---

## THE PROMPT

```
Greenlight Mortgage site — push it live. Three tasks. Report back at the end.

REPO
  ~/Desktop/Greenlight/greenlight-mortgage-site
  branch: main · 25 commits · working tree clean · nothing pushed yet
  remote: https://github.com/ktravis76/GreenlightMortgage.git

===========================================================================
TASK 1 — push to GitHub
===========================================================================
    cd ~/Desktop/Greenlight/greenlight-mortgage-site
    git push -u origin main

It will prompt. Username: ktravis76. Password: a GitHub personal access token
(NOT the account password — GitHub stopped accepting those). If there is no
token, make one at github.com/settings/tokens with `repo` scope. macOS Keychain
stores it after the first success.

The repo is ~33MB because a 17MB homepage video is tracked. That is fine — well
under GitHub's 100MB per-file limit — but the push will take a minute.

If the push is rejected because the remote is not empty, STOP and report back.
Do not force-push. The local history is the only copy of this work.

===========================================================================
TASK 2 — get it deploying on Vercel
===========================================================================
Vercel team:    Team KJR  (team_QwcX1QHwUzCLYA50CuCjpKmt)
Target project: greenlight-mortgage-site  (prj_z1k4kF8T6uHLc9iHr55xLWN1pTYN)

⚠️ DO NOT DEPLOY TO `greenlight-mortgage` (prj_1wYhTkjUvi8cfEMWG7uMxTimr8Ps).
   Similar name, completely different thing — it is the internal Greenlight
   Sales Dashboard the team uses daily. Overwriting it would take out a live
   internal tool.

In the Vercel dashboard, open `greenlight-mortgage-site` → Settings → Git and
connect it to `ktravis76/GreenlightMortgage`, branch `main`. Its last deploy was
a direct upload on 28 Jul and it is probably not git-linked yet, so pushing
alone may not trigger anything.

It is a plain static site. No build command, no install command, no framework —
if Vercel offers to auto-detect one, decline. `vercel.json` in the repo already
sets cleanUrls, the 301 redirect map, and security headers.

⚠️ DO NOT attach greenlightmortgage.com. The domain stays untouched until
   Kenneth has seen and signed off on the finished site. The .vercel.app URL is
   what he is reviewing.

⚠️ Use https://greenlight-mortgage-site.vercel.app — the stable alias — when
   testing forms. Per-deployment URLs look like
   greenlight-mortgage-site-<hash>-team-kjr.vercel.app and are NOT in the Edge
   Function's CORS allowlist, so forms will fail on those with a CORS error that
   looks like a bug but isn't.

===========================================================================
TASK 3 — Supabase Edge Function secrets
===========================================================================
Project: athovwknbwbbqworsbrm  ·  Function: submit-lead (deployed, working)

Leads and applications already save correctly with consent stamped server-side.
What does NOT work yet is email, because no key is set. Right now the site
honestly tells people it could not email them. Setting this turns that on.

Dashboard → Edge Functions → submit-lead → Secrets:

  RESEND_API_KEY   ← needs a Resend account (see below)
  FROM_EMAIL       e.g. Greenlight Mortgage <noreply@glmtg.com>
  NOTIFY_EMAIL     where new applications alert. KT said kenneth@glmtg.com,
                   but allowed_staff has ktravis@glmtg.com — CONFIRM WHICH.
  GHL_WEBHOOK_URL  optional; resumes the GoHighLevel/Konnectd forward
                   (location LRAzmr7bQKMMlXiYfvi6)

For Resend: sign up at resend.com (free tier covers this volume), add and verify
the sending domain, create an API key. Paste it straight into Supabase — it does
not need to go anywhere else, and nobody needs to see it.

No redeploy needed. The function reads the secret on the next request.

===========================================================================
REPORT BACK
===========================================================================
1. Did the push succeed? Any errors?
2. The live URL, and whether the homepage, /loans/va-irrrl and /archive load.
3. Is Vercel now building on push?
4. Which secrets got set — and specifically, is RESEND_API_KEY live?
5. kenneth@glmtg.com or ktravis@glmtg.com for application alerts?
6. While you are in NMLS Consumer Access anyway: look up company NMLS 2426021
   and list the state licenses it actually holds. The site currently advertises
   four (TX, LA, ND, AL). KT said Michigan should be there too but there is no
   license number for it and no source confirms it, so it is being held back.
   Also confirm whether Florida and South Carolina are genuinely gone.
```

---

## Why these cannot be done from here

**The push** needs a GitHub credential. There is none stored on this machine and
the SSH key at `~/.ssh/id_ed25519.pub` is not registered with the account.
Handling somebody's access token is not something an agent should do.

**A direct Vercel deploy** was considered and rejected: the deploy tool takes
files inline, and the payload is 4.6MB across 217 files plus a 17MB video. It
does not fit.

**The Resend account** requires signing up for a third-party service and
handling an API key. That is a person's job, and the key should go straight into
Supabase without passing through a conversation.

## State at handoff

| | |
| --- | --- |
| Pages | 197 |
| Internal links | 18,674, all resolving |
| Chrome consistency | header, footer and brand link identical on all 197 |
| Compliance gate | clean |
| Open items marked on live pages | 210 |
| Commits ready to push | 25 |

Database is hardened and verified, the Edge Function is deployed and tested end
to end, and the follow-up engine schema is in with its guardrails proven. The
only sequence that exists is switched off and nothing can send.
