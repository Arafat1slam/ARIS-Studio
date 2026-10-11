# ARIS Content Automation System — Technical Specification

**Prepared for:** AntiGravity (implementation agent)
**Prepared by:** Claude (architecture/specification)
**Owner:** Aris
**Status:** Ready for implementation
**Target OS:** Windows (local-first deployment)

---

## 1. Purpose

Build a fully local, zero-paid-subscription content automation pipeline that:
- Generates short-form video clips ("Shorts/Reels") from licensed/approved source material.
- Uses Gemini API (within free/existing quota) to generate titles, descriptions, and SEO metadata.
- Auto-publishes to an existing YouTube channel and connected Facebook Page via OAuth.
- Includes the website link (ARIS ANIME) in every post description to drive traffic.
- Pulls SEO signal data via Google Search Console.
- Runs on a configurable schedule, never duplicates a post, and never auto-enables any paid service.
- Requires only periodic human review/maintenance after setup — no daily manual work.

## 2. Non-Negotiable Constraints

These override convenience or "nice to have" shortcuts during implementation:

1. **No paid subscriptions ever auto-enabled.** Every third-party service used must run on its free tier/quota. If a paid tier is required for any step, STOP and flag it to Aris — do not proceed or auto-upgrade.
2. **Copyright compliance.** Only clips explicitly marked "approved/licensed source" (see §6.3) may be used for Shorts generation. No scraping of arbitrary copyrighted anime footage outside the approved source set.
3. **No duplicate posts.** Every piece of content must be fingerprinted (e.g., hash of source clip + generated script) and checked against a local ledger before publishing.
4. **Configurable schedule.** Posting frequency/time must be adjustable via a config file or n8n parameter — not hardcoded.
5. **Quality over quantity.** The pipeline must include a content-quality gate (see §6.1 workflow design) — e.g., minimum clip length, Gemini-generated metadata review step, before publishing is allowed.
6. **Secrets never hardcoded.** All API keys/tokens live in environment variables or a local secrets store, never committed to any repo or left in plaintext n8n workflow JSON.

## 3. High-Level Architecture

```
[Approved Clip Source] 
        |
        v
[FFmpeg Shorts Generator] --> [Gemini API: title/desc/SEO metadata] 
        |                               |
        v                               v
[Duplicate-Check Ledger] <----- [n8n Orchestrator (local, scheduled)]
        |
        v
[YouTube Data API (OAuth)]   [Meta Graph API (Facebook Page, OAuth)]
        |                               |
        v                               v
   Published Shorts              Published FB Post
        |
        v
[Google Search Console API] --> [SEO metrics logged for review]
```

n8n (Community Edition, self-hosted locally) is the central orchestrator — every subsystem below is an n8n workflow or a script n8n calls.

## 4. Technology Stack

| Layer | Tool | Notes |
|---|---|---|
| Orchestration | n8n (Community Edition, self-hosted) | Runs locally on Windows; no n8n Cloud |
| Content generation | Gemini API | Must track usage against Aris's existing free/paid quota — do not exceed without explicit approval |
| Video processing | FFmpeg | Clip trimming, captioning, format conversion for Shorts/Reels |
| Video publishing | YouTube Data API v3 | OAuth 2.0, installed-app or web flow |
| Social publishing | Meta Graph API | Facebook Page access token via OAuth |
| SEO data | Google Search Console API | Read-only metrics pull |
| Secrets | `.env` / Windows Credential Manager (TBD by AntiGravity based on environment audit) | Never plaintext in workflow exports |

## 5. Implementation Phases

AntiGravity must execute these phases **in order**, and must not skip the environment audit or the credential-security step.

### Phase 0 — Environment Audit
- Detect OS version, confirm Windows compatibility.
- Check for existing installs: Node.js (required by n8n), Docker (optional, if containerized n8n is chosen), FFmpeg, Git, Python (if needed for helper scripts).
- Report findings back before installing anything new. Do not silently install major tooling without listing what will be added.

### Phase 1 — n8n Local Setup
- Install n8n Community Edition locally (npm global install or Docker — choose based on Phase 0 findings; prefer the lighter-weight option for a no-dedicated-GPU machine).
- Configure n8n to run on startup or on-demand (confirm with Aris which is preferred — do not assume).
- Verify local n8n editor UI is reachable.

### Phase 2 — Gemini API Integration
- Connect Gemini API using Aris's existing key (supplied securely, not typed into chat/workflow).
- Build an n8n node/workflow step that: takes a clip's context → generates title, description (with website link placeholder), tags, and a short SEO blurb.
- Add a quota-tracking check (log token/request usage) so Aris can see consumption trending toward any paid threshold.

### Phase 3 — Shorts Generation Pipeline (FFmpeg)
- Define the "approved clip source" — a designated local folder or list that Aris manually curates/licenses. AntiGravity should NOT auto-source clips from the public internet.
- FFmpeg workflow: trim to Shorts-compatible length (≤60s), convert to vertical format where needed, optional caption burn-in.
- Output file naming must include a content hash for the duplicate-check step.

### Phase 4 — YouTube OAuth & Publishing
- Implement OAuth 2.0 flow for Aris's existing YouTube channel (one-time authorization, refresh token stored securely).
- n8n workflow step: upload video, attach Gemini-generated title/description (with website link), set as Short, apply configured privacy/schedule settings.

### Phase 5 — Facebook Page OAuth & Publishing
- Implement OAuth flow for the connected Facebook Page via Meta Graph API.
- n8n workflow step: post video + description (with website link) to the Page.

### Phase 6 — SEO Data Pull
- Connect Google Search Console API (read-only) for the ARIS ANIME website property.
- Scheduled pull of key metrics (impressions, clicks, top queries) into a log Aris can review — informs future content topics.

### Phase 7 — Scheduling & Configuration
- Expose schedule (frequency, time windows) as an editable config (n8n Cron node parameters or a config file n8n reads).
- Document how Aris changes the schedule without touching workflow internals.

### Phase 8 — Duplicate Prevention
- Local ledger (simple JSON/SQLite file) recording content hashes of everything already published.
- Every run checks the ledger before publishing; skips/flags duplicates instead of reposting.

### Phase 9 — Secure Credential Management
- All tokens/keys (Gemini, YouTube OAuth, Meta Graph, Search Console) stored outside workflow JSON exports — environment variables or OS credential store.
- No secrets committed to any version control.
- Document the credential rotation/revocation process for Aris.

### Phase 10 — Guardrails for Paid Services
- Explicit check/document per service confirming it is operating on a free tier/quota.
- No workflow step may call a billing/upgrade endpoint automatically.

### Phase 11 — End-to-End Testing
Checklist AntiGravity must verify before declaring the system ready:
- [ ] n8n runs locally and the workflow executes end-to-end without manual intervention.
- [ ] Gemini-generated content (title/description/tags) is produced correctly and includes the website link.
- [ ] A Short is generated via FFmpeg from an approved clip and meets format requirements.
- [ ] Test post succeeds on YouTube (as a Short, correct metadata).
- [ ] Test post succeeds on the Facebook Page.
- [ ] Re-running the pipeline on the same clip does NOT produce a duplicate post (ledger check works).
- [ ] Search Console data pulls successfully and is logged.
- [ ] No step triggered any paid-tier usage or subscription.
- [ ] Schedule can be changed via config without editing workflow logic.

### Phase 12 — Handoff & Monitoring Mode
- Produce a short "operator guide" (separate from this spec) for Aris: how to add new approved clips, how to review/approve content before it posts (if a review gate is included), how to check logs, how to pause automation.
- After this phase, Aris's ongoing role is limited to: reviewing generated content, occasional maintenance (credential renewal, approved-clip updates).

## 6. Security Checklist (apply throughout, not just Phase 9)

- OAuth tokens scoped to minimum required permissions (no broader access than needed to post).
- Refresh tokens stored encrypted or in a protected credential store, not plaintext files.
- Rate-limit / error-handling on every external API call (Gemini, YouTube, Meta, Search Console) so a failure doesn't retry-loop into quota exhaustion.
- Logging must not print full tokens/keys, even in debug mode.

## 7. Assumptions (confirm or correct before/with implementation)

- The website linked in post descriptions is the ARIS ANIME streaming site.
- "Approved clips" means Aris manually curates a local source folder/list of clips cleared for reuse — AntiGravity does not decide what is copyright-safe.
- A content-review gate (Aris approves before auto-publish, at least initially) is desirable but not explicitly specified — AntiGravity should ask Aris whether Phase 1 launches with full auto-publish or a review-first mode.

## 8. Out of Scope (for this phase)

- Any paid ad spend, boosted posts, or paid API tiers.
- Multi-channel expansion beyond the one YouTube channel + one Facebook Page named here.
- Automated sourcing/scraping of new clips from the public internet.
