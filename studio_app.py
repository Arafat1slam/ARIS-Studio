"""
ARIS Studio AI - Desktop Web Application & Control Center
Provides a sleek, modern GUI for:
1. Custom AI Video Editing (Prompt to Rendered Video)
2. 24/7 Autopilot Control & One-Click Publisher
3. Viral Clip Sourcing & Queue Management
Built with 100% native Python standard library for instant zero-dependency execution
and seamless PyInstaller .EXE packaging.
"""

import os
import sys
import json
import glob
import urllib.parse
import subprocess
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(os.path.join(PROJECT_DIR, "scripts"))

import custom_ai_editor

PORT = 8585
RUNNING_LOGS = []

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

    return {
        "status": "online",
        "port": PORT,
        "total_published": len(ledger_records),
        "recent_records": ledger_records[-8:],
        "approved_clips": approved_clips,
        "broll_clips": broll_clips,
        "custom_edits": custom_edits
    }

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ARIS Studio AI ⚡ Desktop Control Center</title>
  <style>
    :root {
      --bg: #090d16;
      --card-bg: rgba(22, 27, 46, 0.7);
      --card-border: rgba(255, 255, 255, 0.08);
      --accent: #6366f1;
      --accent-glow: rgba(99, 102, 241, 0.3);
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --success: #10b981;
      --danger: #ef4444;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    body { background: var(--bg); color: var(--text); min-height: 100vh; padding: 24px; }
    .container { max-width: 1200px; margin: 0 auto; }
    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid var(--card-border); }
    .title { font-size: 26px; font-weight: 800; background: linear-gradient(135deg, #a5b4fc, #6366f1, #38bdf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .badge { background: rgba(16, 185, 129, 0.15); color: var(--success); padding: 6px 12px; border-radius: 9999px; font-size: 13px; font-weight: 600; border: 1px solid rgba(16, 185, 129, 0.3); }
    .nav { display: flex; gap: 12px; margin-bottom: 24px; }
    .nav-btn { background: var(--card-bg); color: var(--text-muted); border: 1px solid var(--card-border); padding: 10px 20px; border-radius: 10px; cursor: pointer; font-size: 15px; font-weight: 600; transition: all 0.2s; }
    .nav-btn.active, .nav-btn:hover { background: var(--accent); color: white; border-color: var(--accent); box-shadow: 0 0 15px var(--accent-glow); }
    .tab-content { display: none; }
    .tab-content.active { display: block; }
    .card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 16px; padding: 24px; margin-bottom: 24px; backdrop-filter: blur(12px); box-shadow: 0 8px 32px rgba(0,0,0,0.3); }
    .card-title { font-size: 18px; font-weight: 700; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
    label { display: block; font-size: 13px; font-weight: 600; color: var(--text-muted); margin-bottom: 8px; }
    input, select, textarea { width: 100%; background: rgba(15, 23, 42, 0.8); border: 1px solid var(--card-border); border-radius: 10px; padding: 12px 14px; color: var(--text); font-size: 14px; margin-bottom: 16px; outline: none; transition: border-color 0.2s; }
    input:focus, select:focus, textarea:focus { border-color: var(--accent); box-shadow: 0 0 0 2px var(--accent-glow); }
    .preset-chips { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
    .chip { background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.3); color: #cbd5e1; padding: 6px 12px; border-radius: 8px; font-size: 12px; cursor: pointer; transition: all 0.2s; }
    .chip:hover { background: var(--accent); color: white; }
    .btn { background: linear-gradient(135deg, #6366f1, #4f46e5); color: white; border: none; padding: 12px 24px; border-radius: 10px; font-size: 15px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; transition: all 0.2s; box-shadow: 0 4px 14px var(--accent-glow); }
    .btn:hover { transform: translateY(-1px); filter: brightness(1.1); }
    .btn-secondary { background: #334155; box-shadow: none; }
    .btn-secondary:hover { background: #475569; }
    .terminal { background: #020617; border: 1px solid #1e293b; border-radius: 10px; padding: 16px; font-family: monospace; font-size: 13px; color: #38bdf8; max-height: 250px; overflow-y: auto; white-space: pre-wrap; margin-top: 16px; }
    video { width: 100%; border-radius: 10px; max-height: 400px; background: #000; margin-top: 12px; border: 1px solid var(--card-border); }
    table { width: 100%; border-collapse: collapse; margin-top: 12px; }
    th, td { text-align: left; padding: 12px; border-bottom: 1px solid var(--card-border); font-size: 13px; }
    th { color: var(--text-muted); font-weight: 600; }
    a { color: #38bdf8; text-decoration: none; }
    a:hover { text-decoration: underline; }
    .status-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; background: var(--success); }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div>
        <div class="title">ARIS Studio AI ⚡</div>
        <div style="color: var(--text-muted); font-size: 14px; margin-top: 4px;">Smart Content Automation & Custom AI Video Studio</div>
      </div>
      <div style="display: flex; gap: 10px; align-items: center;">
        <span class="badge"><span class="status-dot"></span> Engine Online (:8585)</span>
      </div>
    </div>

    <div class="nav">
      <button class="nav-btn active" onclick="showTab('tab-editor')">🎬 Custom AI Video Editor</button>
      <button class="nav-btn" onclick="showTab('tab-autopilot')">🤖 24/7 Autopilot Control</button>
      <button class="nav-btn" onclick="showTab('tab-sourcing')">📥 Viral Anime Clips Queue</button>
    </div>

    <!-- TAB 1: CUSTOM AI VIDEO EDITOR -->
    <div id="tab-editor" class="tab-content active">
      <div class="grid-2">
        <div class="card">
          <div class="card-title">✨ Prompt-to-Video Engine</div>
          <label>১. যে ভিডিওটি এডিট করতে চান সিলেক্ট করুন বা পাথ লিখুন:</label>
          <input type="text" id="custom-video-input" placeholder="e.g. data/broll/broll_peaky4k.mp4 or C:\path\to\video.mp4">
          
          <label>অথবা প্রজেক্টের বিদ্যমান ভিডিও বেছে নিন:</label>
          <select id="quick-video-select" onchange="document.getElementById('custom-video-input').value = this.value">
            <option value="">-- ড্রপডাউন থেকে ভিডিও সিলেক্ট করুন --</option>
          </select>

          <label>২. কীভাবে এডিট করতে চান বাংলায় বা ইংরেজিতে লিখুন:</label>
          <textarea id="custom-prompt" rows="3" placeholder="e.g. 9:16 vertical short বানাও blurred backdrop দিয়ে এবং সাউন্ড বুস্ট করো"></textarea>

          <div class="preset-chips">
            <span class="chip" onclick="setPrompt('Make 9:16 vertical short with ambient blur background and cinematic contrast')">📱 9:16 Viral Short</span>
            <span class="chip" onclick="setPrompt('Enhance cinematic contrast, saturation and add dark aesthetic vignette')">🎨 Cinematic Color</span>
            <span class="chip" onclick="setPrompt('Boost bass by +5dB and dialogue treble with punchy movie theater audio')">🔊 Bass Boost</span>
            <span class="chip" onclick="setPrompt('Apply 1.05x anti-copyright speed micro-tempo shift')">⚡ 1.05x Speed</span>
          </div>

          <button class="btn" id="render-btn" onclick="renderCustomVideo()">⚡ AI দিয়ে ভিডিও এডিট করুন</button>
        </div>

        <div class="card">
          <div class="card-title">📺 লাইভ প্রিভিউ ও রেজাল্ট</div>
          <div id="render-status" style="color: var(--text-muted); font-size: 14px;">কোনো ভিডিও রেন্ডার করা হয়নি। বাঁ দিকের ফর্মে নির্দেশ লিখে রেন্ডার বাটনে চাপুন।</div>
          <div id="video-preview-box" style="display: none;">
            <video id="preview-player" controls></video>
            <div id="render-meta" style="font-size: 13px; color: #a5b4fc; margin-top: 10px;"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 2: AUTOPILOT CONTROL -->
    <div id="tab-autopilot" class="tab-content">
      <div class="card">
        <div class="card-title">🚀 24/7 Autopilot Manual Triggers</div>
        <div style="display: flex; gap: 12px; flex-wrap: wrap;">
          <button class="btn" onclick="triggerRun('ch1')">🎬 Run Channel 1 + Instagram Now</button>
          <button class="btn btn-secondary" onclick="triggerRun('ch2')">🧠 Run Channel 2 (ArisVexx) Now</button>
          <button class="btn btn-secondary" onclick="triggerRun('auto')">🕒 Run Current Scheduled Slot</button>
        </div>
        <div class="terminal" id="autopilot-terminal">Console log will appear here when you run a slot...</div>
      </div>

      <div class="card">
        <div class="card-title">📊 সাম্প্রতিক আপলোড লেজার (Ledger)</div>
        <table id="ledger-table">
          <thead>
            <tr>
              <th>Title</th>
              <th>Channel / Platform</th>
              <th>Status</th>
              <th>Time</th>
              <th>Links</th>
            </tr>
          </thead>
          <tbody id="ledger-body"></tbody>
        </table>
      </div>
    </div>

    <!-- TAB 3: VIRAL SOURCING -->
    <div id="tab-sourcing" class="tab-content">
      <div class="card">
        <div class="card-title">🔥 ভাইরাল অ্যানিমে ক্লিপ কিউ (Approved Clips)</div>
        <p style="color: var(--text-muted); font-size: 14px; margin-bottom: 16px;">
          এই ফোল্ডারে থাকা ক্লিপগুলো ক্লাউড অটো-পাইলট স্বয়ংক্রিয়ভাবে ব্যবহার করে ১টি ১টি করে রেন্ডার ও আপলোড করবে।
        </p>
        <button class="btn" onclick="fetchClips()">📥 নতুন ৩টি ভাইরাল অ্যানিমে ক্লিপ ডাউনলোড করুন</button>
        <div class="terminal" id="sourcing-terminal" style="margin-top: 16px;">Sourcing engine idle.</div>
        <div style="margin-top: 20px;">
          <h4 style="font-size: 15px; margin-bottom: 10px;">বর্তমান কিউতে থাকা ক্লিপসমূহ:</h4>
          <ul id="clips-list" style="padding-left: 20px; font-size: 14px; color: #cbd5e1;"></ul>
        </div>
      </div>
    </div>

  </div>

  <script>
    function showTab(tabId) {
      document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
      document.getElementById(tabId).classList.add('active');
      event.target.classList.add('active');
    }

    function setPrompt(txt) {
      document.getElementById('custom-prompt').value = txt;
    }

    async function loadStatus() {
      try {
        const res = await fetch('/api/status');
        const data = await res.json();
        
        // Populate video select dropdown
        const sel = document.getElementById('quick-video-select');
        sel.innerHTML = '<option value="">-- ড্রপডাউন থেকে ভিডিও সিলেক্ট করুন --</option>';
        [...data.approved_clips, ...data.broll_clips, ...data.custom_edits].forEach(f => {
          let opt = document.createElement('option');
          opt.value = f.includes('broll') ? 'data/broll/' + f : (f.includes('custom') ? 'data/custom_edits/' + f : 'data/approved_clips/' + f);
          opt.textContent = f;
          sel.appendChild(opt);
        });

        // Populate clips list
        const cl = document.getElementById('clips-list');
        cl.innerHTML = '';
        data.approved_clips.forEach(c => {
          let li = document.createElement('li');
          li.textContent = c;
          cl.appendChild(li);
        });

        // Populate ledger table
        const tb = document.getElementById('ledger-body');
        tb.innerHTML = '';
        data.recent_records.reverse().forEach(r => {
          let tr = document.createElement('tr');
          let link = r.youtube_id ? `<a href="https://youtu.be/${r.youtube_id}" target="_blank">YouTube</a>` : '';
          if (r.instagram_id) link += ` | <a href="https://instagram.com/reel/${r.instagram_id}" target="_blank">Instagram</a>`;
          tr.innerHTML = `
            <td>${r.title || 'Untitled'}</td>
            <td>${r.channel || (r.youtube_id ? 'Channel 1 (iταchι Live)' : 'Meta')}</td>
            <td><span class="status-dot"></span> ${r.status || 'published'}</td>
            <td>${(r.published_at || r.timestamp || '').split('T')[0]}</td>
            <td>${link}</td>
          `;
          tb.appendChild(tr);
        });
      } catch (e) {
        console.error(e);
      }
    }

    async function renderCustomVideo() {
      const vPath = document.getElementById('custom-video-input').value.trim();
      const prompt = document.getElementById('custom-prompt').value.trim();
      const status = document.getElementById('render-status');
      const btn = document.getElementById('render-btn');

      if (!vPath || !prompt) {
        alert('অনুগ্রহ করে ভিডিও পাথ এবং আপনার প্রম্পট লিখুন!');
        return;
      }

      btn.disabled = true;
      btn.textContent = '⏳ AI ভিডিও তৈরি করছে (অনুগ্রহ করে অপেক্ষা করুন)...';
      status.textContent = 'AI নির্দেশ বিশ্লেষণ ও FFmpeg দিয়ে হাই-কোয়ালিটি ভিডিও রেন্ডার করছে...';

      try {
        const res = await fetch('/api/custom_edit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ video_path: vPath, prompt: prompt })
        });
        const data = await res.json();
        if (data.success) {
          status.innerHTML = `<span style="color: #10b981; font-weight: 600;">✅ রেন্ডার সফল হয়েছে!</span><br>${data.plan.explanation}`;
          document.getElementById('video-preview-box').style.display = 'block';
          const p = document.getElementById('preview-player');
          p.src = '/video/' + data.filename;
          p.load();
          document.getElementById('render-meta').innerHTML = `রেজোলিউশন: <b>${data.resolution}</b> | সাইজ: <b>${data.size_mb} MB</b> | দৈর্ঘ্য: <b>${data.duration.toFixed(1)}s</b>`;
          loadStatus();
        } else {
          status.innerHTML = `<span style="color: #ef4444;">❌ এরর: ${data.error}</span>`;
        }
      } catch (err) {
        status.innerHTML = `<span style="color: #ef4444;">❌ এরর: ${err.message}</span>`;
      } finally {
        btn.disabled = false;
        btn.textContent = '⚡ AI দিয়ে ভিডিও এডিট করুন';
      }
    }

    async function triggerRun(target) {
      const term = document.getElementById('autopilot-terminal');
      term.textContent = `[*] Starting ${target.toUpperCase()} run in background...\\n`;
      try {
        const res = await fetch('/api/run_slot', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ target: target })
        });
        const data = await res.json();
        term.textContent = data.output || 'Execution finished.';
        loadStatus();
      } catch (err) {
        term.textContent = `Error: ${err.message}`;
      }
    }

    async function fetchClips() {
      const term = document.getElementById('sourcing-terminal');
      term.textContent = '[*] Fetching trending anime clips online...\\n';
      try {
        const res = await fetch('/api/fetch_clips', { method: 'POST' });
        const data = await res.json();
        term.textContent = data.output || 'Finished.';
        loadStatus();
      } catch (err) {
        term.textContent = `Error: ${err.message}`;
      }
    }

    window.onload = loadStatus;
  </script>
</body>
</html>
"""

class StudioRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
            return

        if path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(get_system_status()).encode("utf-8"))
            return

        if path.startswith("/video/"):
            filename = os.path.basename(path)
            # search in custom_edits, broll, approved_clips
            candidates = [
                os.path.join(PROJECT_DIR, "data", "custom_edits", filename),
                os.path.join(PROJECT_DIR, "data", "approved_clips", filename),
                os.path.join(PROJECT_DIR, "data", "broll", filename)
            ]
            target_file = next((f for f in candidates if os.path.exists(f)), None)
            if target_file:
                self.send_response(200)
                self.send_header("Content-Type", "video/mp4")
                self.send_header("Content-Length", str(os.path.getsize(target_file)))
                self.end_headers()
                with open(target_file, "rb") as vf:
                    self.wfile.write(vf.read())
                return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        data = json.loads(body) if body else {}

        if path == "/api/custom_edit":
            video_path = data.get("video_path")
            if not os.path.isabs(video_path):
                video_path = os.path.join(PROJECT_DIR, video_path)
            prompt = data.get("prompt", "")
            
            res = custom_ai_editor.execute_custom_edit(video_path, prompt)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        if path == "/api/run_slot":
            target = data.get("target", "ch1")
            script = os.path.join(PROJECT_DIR, "scripts", "run_cloud_slot.py")
            proc = subprocess.run([sys.executable, script, target], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": proc.returncode == 0, "output": proc.stdout}).encode("utf-8"))
            return

        if path == "/api/fetch_clips":
            script = os.path.join(PROJECT_DIR, "scripts", "fetch_viral_clips.py")
            proc = subprocess.run([sys.executable, script, "3"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": proc.returncode == 0, "output": proc.stdout}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

def main():
    print("=" * 65)
    print("  ARIS Studio AI - Desktop Web Application & Control Center")
    print(f"  Access live UI in your browser at: http://localhost:{PORT}")
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
