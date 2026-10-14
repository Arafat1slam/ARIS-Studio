"""
ARIS Studio AI - Desktop Backend & React App Server
Serves the React frontend (frontend/dist/) and exposes REST APIs for:
1. Custom AI Video Editing (Prompt to Rendered Video)
2. After Effects Bridge & AI ExtendScript Automation (inspired by aftereffects-mcp)
3. 24/7 Autopilot Control & One-Click Multi-Platform Publisher
4. Viral Anime Sourcing Engine
"""

import os
import sys
import json
import glob
import urllib.parse
import subprocess
import mimetypes
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(os.path.join(PROJECT_DIR, "scripts"))

import custom_ai_editor
import aftereffects_bridge
import copyright_remover
import animeclips_fetcher
import channel1_anime_shorts
import channel2_dark_psychology
import quality_control
import premiere_automation

PORT = 8585
FRONTEND_DIST = os.path.join(PROJECT_DIR, "frontend", "dist")

def get_system_status():
    ledger_path = os.path.join(PROJECT_DIR, "config", "ledger.json")
    ledger_records = []
    if os.path.exists(ledger_path):
        try:
            with open(ledger_path, "r", encoding="utf-8") as f:
                ledger_records = json.load(f).get("records", [])
        except Exception:
            pass

    approved_clips = [os.path.basename(f) for f in glob.glob(os.path.join(PROJECT_DIR, "data", "approved_clips", "*.mp4"))]
    broll_clips = [os.path.basename(f) for f in glob.glob(os.path.join(PROJECT_DIR, "data", "broll", "*.mp4"))]
    custom_edits = [os.path.basename(f) for f in glob.glob(os.path.join(PROJECT_DIR, "data", "custom_edits", "*.mp4"))]
    clean_clips = [os.path.basename(f) for f in glob.glob(os.path.join(PROJECT_DIR, "data", "copyright_free", "*.mp4"))]

    return {
        "status": "online",
        "port": PORT,
        "total_published": len(ledger_records),
        "recent_records": ledger_records[-15:],
        "approved_clips": approved_clips,
        "broll_clips": broll_clips,
        "custom_edits": custom_edits,
        "clean_clips": clean_clips
    }

class StudioRequestHandler(BaseHTTPRequestHandler):
    def end_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # 1. API: System Status
        if path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(get_system_status()).encode("utf-8"))
            return

        # 2. API: After Effects & Premiere Pro Status
        if path == "/api/ae/status" or path == "/api/premiere/status":
            status = aftereffects_bridge.check_bridge_connection()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(status).encode("utf-8"))
            return

        # 2.05 API: After Effects Templates List
        if path == "/api/ae/templates":
            templates = aftereffects_bridge.list_available_templates()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(templates).encode("utf-8"))
            return

        # 2.1 API: AnimeClips.online Titles List
        if path == "/api/animeclips/titles":
            titles = animeclips_fetcher.get_all_titles()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(titles).encode("utf-8"))
            return

        # 2.2 API: AnimeClips.online Clips by Slug
        if path.startswith("/api/animeclips/clips"):
            query_params = urllib.parse.parse_qs(parsed.query)
            slug = query_params.get("slug", ["a-silent-voice"])[0]
            clips = animeclips_fetcher.get_title_clips(slug)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(clips).encode("utf-8"))
            return

        # 3. Stream Video Files for React Player
        if path.startswith("/video/"):
            filename = os.path.basename(path)
            candidates = [
                os.path.join(PROJECT_DIR, "data", "copyright_free", filename),
                os.path.join(PROJECT_DIR, "data", "custom_edits", filename),
                os.path.join(PROJECT_DIR, "data", "approved_clips", filename),
                os.path.join(PROJECT_DIR, "data", "broll", filename)
            ]
            target_file = next((f for f in candidates if os.path.exists(f)), None)
            if target_file:
                size = os.path.getsize(target_file)
                self.send_response(200)
                self.send_header("Content-Type", "video/mp4")
                self.send_header("Content-Length", str(size))
                self.send_header("Accept-Ranges", "bytes")
                self.end_cors_headers()
                self.end_headers()
                with open(target_file, "rb") as vf:
                    self.wfile.write(vf.read())
                return
            else:
                self.send_response(404)
                self.end_headers()
                return

        # 4. Serve React App Assets (/assets/...)
        if path.startswith("/assets/"):
            asset_file = os.path.join(FRONTEND_DIST, path.lstrip("/"))
            if os.path.exists(asset_file) and os.path.isfile(asset_file):
                mime, _ = mimetypes.guess_type(asset_file)
                self.send_response(200)
                self.send_header("Content-Type", mime or "application/octet-stream")
                self.end_headers()
                with open(asset_file, "rb") as f:
                    self.wfile.write(f.read())
                return

        # 5. Serve React index.html for Root and SPA fallback
        index_file = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index_file):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(index_file, "rb") as f:
                self.wfile.write(f.read())
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8", errors="replace") if length > 0 else "{}"
        try:
            data = json.loads(body) if body else {}
        except Exception:
            try:
                data = json.loads(body.replace("\\", "\\\\"))
            except Exception:
                data = {}

        # API: Custom AI Video Edit
        if path == "/api/custom_edit":
            video_path = data.get("video_path", "").strip()
            if not os.path.isabs(video_path):
                video_path = os.path.join(PROJECT_DIR, video_path)
            prompt = data.get("prompt", "")
            
            res = custom_ai_editor.execute_custom_edit(video_path, prompt)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        # API: After Effects Generate ExtendScript (.jsx)
        if path == "/api/ae/generate_jsx":
            prompt = data.get("prompt", "")
            comp_type = data.get("comp_type", "9:16")
            plan = aftereffects_bridge.generate_extendscript_with_ai(prompt, comp_type)
            dispatch_res = aftereffects_bridge.save_and_dispatch_jsx(plan.get("jsx_code", ""))
            
            out = {
                "success": True,
                "plan": plan,
                "filename": dispatch_res.get("filename"),
                "file_path": dispatch_res.get("file_path"),
                "bridge_status": dispatch_res.get("bridge_status"),
                "dispatched_live": dispatch_res.get("dispatched_to_ae_live")
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(out).encode("utf-8"))
            return

        # API: Autopilot Manual Run Slot
        if path == "/api/run_slot":
            target = data.get("target", "ch1")
            script = os.path.join(PROJECT_DIR, "scripts", "run_cloud_slot.py")
            proc = subprocess.run([sys.executable, script, target], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"success": proc.returncode == 0, "output": proc.stdout}).encode("utf-8"))
            return

        # API: Fetch Fresh Viral Clips
        if path == "/api/fetch_clips":
            script = os.path.join(PROJECT_DIR, "scripts", "fetch_viral_clips.py")
            proc = subprocess.run([sys.executable, script, "3"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"success": proc.returncode == 0, "output": proc.stdout}).encode("utf-8"))
            return

        # API: Copyright Risk Analysis
        if path == "/api/copyright/analyze":
            video_path = data.get("video_path", "").strip()
            if not video_path:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": "No video path or URL provided"}).encode("utf-8"))
                return

            is_url = video_path.startswith("http://") or video_path.startswith("https://")
            if not is_url:
                if not os.path.isabs(video_path):
                    video_path = os.path.join(PROJECT_DIR, video_path)
                if not os.path.exists(video_path):
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.end_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": f"File not found: {video_path}"}).encode("utf-8"))
                    return

            try:
                res = copyright_remover.analyze_copyright_risks(video_path)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(res).encode("utf-8"))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

        # API: Copyright Neutralization & Watermarking
        if path == "/api/copyright/process":
            video_path = data.get("video_path", "").strip()
            if not video_path:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": "No video path or URL provided"}).encode("utf-8"))
                return

            is_url = video_path.startswith("http://") or video_path.startswith("https://")
            if not is_url:
                if not os.path.isabs(video_path):
                    video_path = os.path.join(PROJECT_DIR, video_path)
                if not os.path.exists(video_path):
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.end_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": f"File not found: {video_path}"}).encode("utf-8"))
                    return

            watermark_text = (data.get("watermark") or data.get("watermark_text") or "ARIS").strip() or "ARIS"
            mode = data.get("mode", "9:16_short")
            tempo = float(data.get("tempo", 1.04))

            try:
                res = copyright_remover.process_copyright_removal(video_path, watermark_text, mode, tempo)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(res).encode("utf-8"))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_cors_headers()
                self.end_headers()
        # API: Pipeline - Channel 1 Anime Shorts
        if path == "/api/pipeline/channel1":
            slug = data.get("slug", "a-silent-voice")
            custom_clip = data.get("clip_path")
            res = channel1_anime_shorts.produce_channel1_short(anime_slug=slug, custom_clip_path=custom_clip)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        # API: Pipeline - Channel 2 Dark Psychology
        if path == "/api/pipeline/channel2":
            res = channel2_dark_psychology.produce_channel2_short()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        # API: AnimeClips.online Download Single Clip
        if path == "/api/animeclips/download":
            clip_info = data.get("clip")
            target_dir = data.get("target_dir", os.path.join(PROJECT_DIR, "data", "approved_clips"))
            dl_path = animeclips_fetcher.download_clip(clip_info, target_dir)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"success": bool(dl_path), "path": dl_path}).encode("utf-8"))
            return

        # API: Quality Control Audit
        if path == "/api/qc/audit":
            vpath = data.get("video_path", "").strip()
            if not os.path.isabs(vpath):
                vpath = os.path.join(PROJECT_DIR, vpath)
            res = quality_control.audit_video(vpath)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        # API: Quality Control Auto-Remediation
        if path == "/api/qc/remediate":
            vpath = data.get("video_path", "").strip()
            if not os.path.isabs(vpath):
                vpath = os.path.join(PROJECT_DIR, vpath)
            res = quality_control.remediate_video(vpath)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        # API: Adobe Premiere Pro XML & ExtendScript Export
        if path == "/api/premiere/export":
            clip_paths = data.get("clip_paths", [])
            title = data.get("title", "ARIS AI Short")
            vo_path = data.get("voiceover_path")
            bgm_path = data.get("bgm_path")
            res = premiere_automation.build_pro_editing_package(clip_paths, voiceover_path=vo_path, bgm_path=bgm_path, title=title)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, **res}).encode("utf-8"))
            return

        # API: Launch Adobe Premiere Pro 2026
        if path == "/api/premiere/launch":
            ppro_path = "C:\\Program Files\\Adobe\\Adobe Premiere Pro 2026\\Adobe Premiere Pro.exe"
            if os.path.exists(ppro_path):
                subprocess.Popen([ppro_path])
                res = {"success": True, "message": "Adobe Premiere Pro 2026 launched successfully!"}
            else:
                res = {"success": False, "error": "Premiere Pro executable not found in standard path"}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

def main():
    print("=" * 65)
    print("  ARIS Studio AI - React Desktop Web App & Backend Server")
    print(f"  Live UI running at: http://localhost:{PORT}")
    print("=" * 65)
    
    server = HTTPServer(("127.0.0.1", PORT), StudioRequestHandler)
    try:
        import webbrowser
        webbrowser.open(f"http://localhost:{PORT}")
    except Exception:
        pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Shutting down ARIS Studio.")
        server.server_close()

if __name__ == "__main__":
    main()
