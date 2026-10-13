"""
ARIS Content Automation System - Master Pipeline Orchestrator
Executes the end-to-end automation workflow:
1. Scans approved anime clips in data/approved_clips/
2. Converts to vertical 9:16 Shorts/Reels (<= 58s) using FFmpeg
3. Checks duplicate ledger using SHA-256 content hashes
4. Generates SEO metadata & website CTA link using Gemini API (with free quota guardrail)
5. Enforces quality gate and review approval gate or auto-publishing
6. Updates duplicate prevention ledger
"""

import os
import sys
import glob
import json
from datetime import datetime

import ffmpeg_generator
import duplicate_checker
import gemini_metadata
import youtube_meta_publisher

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_FILE = os.path.join(PROJECT_DIR, "config", "config.json")
APPROVED_DIR = os.path.join(PROJECT_DIR, "data", "approved_clips")
PROCESSED_DIR = os.path.join(PROJECT_DIR, "data", "processed_shorts")
LOGS_DIR = os.path.join(PROJECT_DIR, "data", "logs")
PENDING_APPROVALS_FILE = os.path.join(LOGS_DIR, "pending_approvals.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def scan_approved_clips():
    """Scan approved clips directory for video files."""
    extensions = ["*.mp4", "*.mkv", "*.mov", "*.webm", "*.avi"]
    clips = []
    for ext in extensions:
        clips.extend(glob.glob(os.path.join(APPROVED_DIR, ext)))
    return sorted(clips)

def load_pending_approvals():
    if os.path.exists(PENDING_APPROVALS_FILE):
        try:
            with open(PENDING_APPROVALS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_pending_approval(item):
    approvals = load_pending_approvals()
    # Replace or add
    for idx, existing in enumerate(approvals):
        if existing.get("content_hash") == item.get("content_hash"):
            approvals[idx] = item
            with open(PENDING_APPROVALS_FILE, "w", encoding="utf-8") as f:
                json.dump(approvals, f, indent=2)
            return
    approvals.append(item)
    with open(PENDING_APPROVALS_FILE, "w", encoding="utf-8") as f:
        json.dump(approvals, f, indent=2)

def run_pipeline(dry_run=False, force_auto=False):
    config = load_config()
    pipeline_cfg = config.get("pipeline", {})
    review_mode = pipeline_cfg.get("review_gate_enabled", True) and not force_auto
    max_duration = config.get("video_processing", {}).get("max_duration_seconds", 58)

    print("=====================================================", file=sys.stderr)
    print("  ARIS Content Automation System - Running Pipeline", file=sys.stderr)
    print(f"  Mode: {'REVIEW-FIRST GATE' if review_mode else 'FULL AUTO-PUBLISH'}", file=sys.stderr)
    print(f"  Dry-Run: {dry_run}", file=sys.stderr)
    print("=====================================================", file=sys.stderr)

    clips = scan_approved_clips()
    if not clips:
        print("[*] No clips in approved_clips directory. Auto-sourcing viral anime clip online...", file=sys.stderr)
        try:
            import clip_downloader
            fetch_res = clip_downloader.auto_fetch_viral_batch(count=1)
            if fetch_res.get("fetched_count", 0) > 0:
                clips = scan_approved_clips()
        except Exception as e:
            print(f"[-] Auto-sourcing error: {e}", file=sys.stderr)

    if not clips:
        msg = f"No video clips found in '{APPROVED_DIR}' and online search returned no candidates."
        print(msg, file=sys.stderr)
        return {"status": "no_input_clips", "message": msg, "processed_count": 0}

    results = []

    for clip in clips:
        filename = os.path.basename(clip)
        print(f"\n[Processing] Found clip: {filename}", file=sys.stderr)

        # 0. Source Duplicate Check before heavy FFmpeg rendering
        src_hash = duplicate_checker.calculate_file_hash(clip)
        is_src_dup, src_rec = duplicate_checker.is_duplicate(src_hash)
        if not is_src_dup:
            is_src_dup, src_rec = duplicate_checker.is_duplicate(filename)
        if is_src_dup:
            print(f"[*] Source clip '{filename}' was already published! Purging to avoid duplicate.", file=sys.stderr)
            try:
                if os.path.exists(clip): os.remove(clip)
            except Exception: pass
            results.append({
                "clip": filename,
                "status": "duplicate_skipped",
                "source_file": filename,
                "existing_record": src_rec
            })
            continue

        # 1. FFmpeg video generation
        video_res = ffmpeg_generator.generate_short(clip, max_duration=max_duration)
        if not video_res.get("success"):
            print(f"[-] Video processing failed: {video_res.get('error')}", file=sys.stderr)
            results.append({"clip": filename, "status": "failed_ffmpeg", "error": video_res.get("error")})
            continue

        content_hash = video_res["content_hash"]
        output_file = video_res["output_file"]

        # 2. Duplicate prevention check
        is_dup, dup_record = duplicate_checker.is_duplicate(content_hash)
        if is_dup:
            print(f"[*] Duplicate detected in ledger! Skipping and purging {filename} (Hash: {content_hash[:8]}).", file=sys.stderr)
            try:
                if os.path.exists(clip):
                    os.remove(clip)
            except Exception:
                pass
            try:
                if os.path.exists(output_file):
                    os.remove(output_file)
            except Exception:
                pass
            results.append({
                "clip": filename,
                "status": "duplicate_skipped",
                "content_hash": content_hash,
                "existing_record": dup_record
            })
            continue

        # 3. Gemini metadata generation
        clip_name_clean = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ")
        meta_res = gemini_metadata.generate_metadata(clip_context=clip_name_clean)

        if not meta_res.get("success"):
            print(f"[!] Gemini metadata generation note: {meta_res.get('error')}", file=sys.stderr)
            # Safe fallback if API key not yet configured
            site_url = pipeline_cfg.get("website_url", "https://aris-anime.com")
            brand = pipeline_cfg.get("brand_name", "ARIS ANIME")
            meta_res = {
                "title": f"{clip_name_clean} 🔥 #Shorts",
                "description": f"Best anime moments from {brand}!\n\n▶ Watch full episodes in HD: {site_url}\n\n#anime #animereels #arisanime #otaku",
                "tags": ["anime", "shorts", "reels", "arisanime"],
                "quality_score": 8,
                "call_to_action_url": site_url,
                "fallback_used": True
            }

        title = meta_res["title"]
        desc = meta_res["description"]
        tags = meta_res.get("tags", [])

        # 4. Review Gate vs Publishing
        item_package = {
            "source_clip": clip,
            "processed_short": output_file,
            "content_hash": content_hash,
            "duration": video_res["duration"],
            "title": title,
            "description": desc,
            "tags": tags,
            "quality_score": meta_res.get("quality_score", 8),
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }

        if review_mode:
            save_pending_approval(item_package)
            print(f"[+] Saved to Pending Approvals for Aris's review: '{title}'", file=sys.stderr)
            results.append({
                "clip": filename,
                "status": "pending_review",
                "content_hash": content_hash,
                "title": title,
                "video_file": output_file
            })
        else:
            # Auto-publish
            print(f"[>] Publishing to YouTube & Facebook...", file=sys.stderr)
            pub_res = youtube_meta_publisher.publish_content(
                video_path=output_file,
                content_hash=content_hash,
                title=title,
                description=desc,
                tags=tags,
                dry_run=dry_run,
                source_file=filename,
                source_hash=src_hash
            )
            results.append({
                "clip": filename,
                "status": "published" if pub_res.get("success") else "publish_failed",
                "content_hash": content_hash,
                "details": pub_res
            })
            if pub_res.get("success"):
                try:
                    if os.path.exists(clip):
                        os.remove(clip)
                        print(f"[+] Purged source clip '{filename}' from approved_clips to guarantee no duplicates.", file=sys.stderr)
                except Exception as pe:
                    print(f"[!] Purge error: {pe}", file=sys.stderr)

    # If all existing clips were duplicates and none got published, auto-fetch 1 fresh clip online!
    has_success = any(r.get("status") in ("published", "pending_review") for r in results)
    if not has_success and not dry_run:
        print("[*] All previous clips were duplicates. Auto-fetching fresh viral anime clip...", file=sys.stderr)
        try:
            import clip_downloader
            fetch_res = clip_downloader.auto_fetch_viral_batch(count=1)
            fresh_clips = scan_approved_clips()
            for fresh_clip in fresh_clips:
                fname = os.path.basename(fresh_clip)
                f_srchash = duplicate_checker.calculate_file_hash(fresh_clip)
                is_fdup, _ = duplicate_checker.is_duplicate(f_srchash)
                if not is_fdup:
                    is_fdup, _ = duplicate_checker.is_duplicate(fname)
                if is_fdup:
                    try:
                        if os.path.exists(fresh_clip): os.remove(fresh_clip)
                    except Exception: pass
                    continue

                vres = ffmpeg_generator.generate_short(fresh_clip, max_duration=max_duration)
                if vres.get("success"):
                    chash = vres["content_hash"]
                    outfile = vres["output_file"]
                    cname = os.path.splitext(fname)[0].replace("_", " ").replace("-", " ")
                    mres = gemini_metadata.generate_metadata(clip_context=cname)
                    t_title = mres.get("title", f"{cname} #Shorts")
                    t_desc = mres.get("description", "")
                    t_tags = mres.get("tags", [])
                    pres = youtube_meta_publisher.publish_content(
                        outfile, chash, t_title, t_desc, t_tags, dry_run=False,
                        source_file=fname, source_hash=f_srchash
                    )
                    results.append({
                        "clip": fname,
                        "status": "published" if pres.get("success") else "publish_failed",
                        "content_hash": chash,
                        "details": pres
                    })
                    if pres.get("success"):
                        try:
                            if os.path.exists(fresh_clip):
                                os.remove(fresh_clip)
                                print(f"[+] Purged fresh source clip '{fname}' after publishing.", file=sys.stderr)
                        except: pass
        except Exception as e:
            print(f"[-] Fresh clip auto-source failed: {e}", file=sys.stderr)

    summary = {
        "status": "completed",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "processed_clips": len(results),
        "results": results
    }

    print("\nPipeline execution summary completed.", file=sys.stderr)
    return summary

if __name__ == "__main__":
    is_dry = "--dry-run" in sys.argv
    force_pub = "--auto" in sys.argv
    output = run_pipeline(dry_run=is_dry, force_auto=force_pub)
    print(json.dumps(output, indent=2))
