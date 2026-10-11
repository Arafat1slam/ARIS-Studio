# ARIS Content Automation System — Operator Guide

**Owner:** Aris  
**System:** ARIS Content Automation System  
**Deployment:** Local-first (Windows)

---

## 🚀 Quick Start in 3 Steps

### 1. Add Approved Anime Clips
Place your licensed/cleared anime video clips (`.mp4`, `.mkv`, `.mov`) into:
```
data\approved_clips\
```
> [!IMPORTANT]
> **Copyright Compliance:** Only place clips you have permission or license to use. The automation will never scrape or download external copyrighted footage on its own.

### 2. Configure Your Free API Keys
Make a copy of `.env.example` named `.env` in the project root:
```bash
copy .env.example .env
```
Open `.env` and fill in:
- **`GEMINI_API_KEY`**: Your free Gemini API key from [Google AI Studio](https://aistudio.google.com/).
- **`WEBSITE_URL`**: Your streaming site URL (e.g. `https://aris-anime.com`) — this is automatically embedded into every generated post description.
- **`YOUTUBE_*`**: OAuth 2.0 credentials for your YouTube channel.
- **`META_*`**: Facebook Page Access Token.
- **`GSC_*`**: Google Search Console credentials (for SEO signal pulls).

### 3. Run the Automation
You have three easy ways to run:
- **Start n8n Server (Continuous Scheduled Orchestrator):**  
  Double-click `start_n8n.bat` or run:
  ```cmd
  n8n start
  ```
  Then open **http://localhost:5678** in your browser.
- **Run Pipeline On-Demand:**  
  Double-click `run_pipeline.bat` or run:
  ```cmd
  python scripts\pipeline_orchestrator.py
  ```
- **Review & Approve Pending Posts:**  
  Double-click `review_approvals.bat` or run:
  ```cmd
  python scripts\review_manager.py
  ```

---

## 🛡️ Non-Negotiable System Guardrails

1. **Zero Paid Subscriptions:**  
   The system strictly operates on free quotas. Daily request counters in `data/logs/quota_tracker.json` automatically halt calls before hitting any paid threshold.
2. **Duplicate Prevention:**  
   Every video generated is fingerprinted with a SHA-256 hash. The ledger `config/ledger.json` records every published clip. If you run the pipeline twice on the same clip, it will be skipped automatically.
3. **Content Review Gate (Default):**  
   By default, the pipeline runs in **Review Mode**. It trims the clip, creates the vertical Short with background blur, generates the Gemini title and SEO description (with your website link), and saves it to `data/logs/pending_approvals.json`. It will **never** publish to your channels until you inspect and approve it.

---

## ⚙️ How to Change the Schedule or Settings

Open [config/config.json](file:///d:/ALL%20PROJECT/n8n/config/config.json):
```json
{
  "pipeline": {
    "mode": "review",                     // "review" for approval gate, "auto" for direct posting
    "review_gate_enabled": true,
    "schedule_cron": "0 14 * * *",        // Runs daily at 2:00 PM (14:00)
    "website_url": "https://aris-anime.com",
    "brand_name": "ARIS ANIME"
  },
  "video_processing": {
    "max_duration_seconds": 58            // Guarantees <=60s Shorts/Reels eligibility
  }
}
```
You can adjust:
- **`schedule_cron`**: Change posting time without touching any code.
- **`review_gate_enabled`**: Set to `false` when you are confident and want fully autonomous publishing.
- **`website_url`**: Change the destination URL promoted in every video description.

---

## 📊 Viewing Logs and Metrics

- **Duplicate Ledger:** [config/ledger.json](file:///d:/ALL%20PROJECT/n8n/config/ledger.json)
- **Gemini Daily Quota Log:** `data\logs\quota_tracker.json`
- **Search Console SEO Report:** `data\logs\seo_metrics.json`
- **Pending Approvals Queue:** `data\logs\pending_approvals.json`

---

## 🛑 How to Pause or Stop Automation

- If running via batch script: Close the `start_n8n.bat` terminal window or press `Ctrl + C`.
- In n8n Editor UI (http://localhost:5678): Toggle the workflow switch from **Active** to **Inactive**.
