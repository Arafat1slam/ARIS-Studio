# ARIS Content Automation System

A local-first, zero-paid-subscription content automation pipeline for anime Shorts and Reels.

## 🎯 Architecture
```
[Approved Clip Source] (data/approved_clips/)
        │
        ▼
[FFmpeg Shorts Generator] (9:16 vertical, <=58s) ──► [Gemini API] (Title, SEO desc, CTA link)
        │                                                     │
        ▼                                                     ▼
[Duplicate Ledger] (SHA-256 Check) ◄────────────────── [n8n Local Orchestrator]
        │
        ▼
[YouTube Shorts & Meta Reels Publisher]
        │
        ▼
[Google Search Console] (SEO Signal Tracker)
```

## 📁 Repository Structure
```
├── .env.example              # Secrets template (never committed)
├── .gitignore                # Safeguard against committing secrets, data, and models
├── OPERATOR_GUIDE.md         # Daily operator handbook for Aris
├── ARIS-Content-Automation-System-Spec.md # Technical specification
├── config/
│   ├── config.json           # Editable schedule, brand URL, video settings
│   └── ledger.json           # SHA-256 duplicate prevention ledger
├── data/
│   ├── approved_clips/       # Source anime clips manually approved by Aris
│   ├── processed_shorts/     # Generated 9:16 vertical videos (<=58s)
│   └── logs/                 # Quota tracker, SEO metrics, pending reviews
├── scripts/
│   ├── ffmpeg_generator.py   # Vertical video processor with background blur
│   ├── duplicate_checker.py  # SHA-256 ledger fingerprinting
│   ├── gemini_metadata.py    # Gemini title/desc/SEO generator & quota guardrail
│   ├── gsc_metrics.py        # Search Console read-only SEO puller
│   ├── youtube_meta_publisher.py # Multi-platform publisher (YouTube & Facebook)
│   ├── pipeline_orchestrator.py # Master pipeline execution script
│   └── review_manager.py     # Interactive review CLI
├── workflows/
│   ├── aris_content_automation_pipeline.json # n8n workflow for content generation
│   └── gsc_seo_tracker.json  # n8n workflow for SEO metrics tracking
├── tools/
│   └── ffmpeg.exe            # High-performance local FFmpeg v7.1
├── start_n8n.bat             # One-click n8n launcher
├── run_pipeline.bat          # One-click pipeline runner
└── review_approvals.bat      # One-click review & publish launcher
```

## 🚀 Getting Started
1. Run `start_n8n.bat` or `n8n start` to open the local web UI at `http://localhost:5678`.
2. Add your approved video clips to `data/approved_clips/`.
3. Fill your API keys in `.env` (copied from `.env.example`).
4. Read [OPERATOR_GUIDE.md](file:///d:/ALL%20PROJECT/n8n/OPERATOR_GUIDE.md) for full instructions.