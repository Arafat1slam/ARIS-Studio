"""
ARIS After Effects Bridge & AI ExtendScript Automation Engine
Directly integrated with solomondivyananth/aftereffects-mcp:
1. Local repository at tools/aftereffects-mcp
2. CEP Bridge panel linked to %APPDATA%/Adobe/CEP/extensions/com.aemcpbridge
3. Direct bidirectional RPC to running Adobe After Effects instance via CEP Bridge (port 7788)
4. AI-driven ExtendScript (.jsx) generation & live execution
5. Automated Comp creation (9:16 vertical shorts, 16:9 widescreen, 1:1 square)
"""

import os
import sys
import json
import glob
import subprocess
import urllib.request
import urllib.error
from datetime import datetime

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_FILE = os.path.join(PROJECT_DIR, ".env")
AE_SCRIPTS_DIR = os.path.join(PROJECT_DIR, "data", "ae_scripts")
AE_PREVIEWS_DIR = os.path.join(PROJECT_DIR, "data", "ae_previews")
AE_MCP_DIR = os.path.join(PROJECT_DIR, "aftereffects-mcp") if os.path.exists(os.path.join(PROJECT_DIR, "aftereffects-mcp")) else os.path.join(PROJECT_DIR, "tools", "aftereffects-mcp")

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = int(os.environ.get("AE_BRIDGE_PORT", 7788))

def load_env():
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k not in os.environ:
                        os.environ[k] = v

def get_bridge_token():
    if os.environ.get("AE_BRIDGE_TOKEN"):
        return os.environ.get("AE_BRIDGE_TOKEN")
    home = os.path.expanduser("~")
    state_path = os.path.join(home, ".ae-mcp-bridge.json")
    if os.path.exists(state_path):
        try:
            with open(state_path, "r", encoding="utf-8") as f:
                return json.load(f).get("token", "")
        except Exception:
            pass
    return ""

def is_panel_installed():
    """Check if the CEP extension com.aemcpbridge is linked in AppData."""
    appdata = os.environ.get("APPDATA", os.path.join(os.path.expanduser("~"), "AppData", "Roaming"))
    ext_path = os.path.join(appdata, "Adobe", "CEP", "extensions", "com.aemcpbridge")
    return os.path.exists(ext_path)

def install_or_link_panel():
    """Runs bin/install-panel.js --link from tools/aftereffects-mcp."""
    install_script = os.path.join(AE_MCP_DIR, "bin", "install-panel.js")
    if os.path.exists(install_script):
        try:
            res = subprocess.run(["node", install_script, "--link"], cwd=AE_MCP_DIR, capture_output=True, text=True)
            return {"success": res.returncode == 0, "output": res.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}
    return {"success": False, "error": "install-panel.js not found"}

def find_after_effects_exe():
    """Look for AfterFX.exe or aerender.exe on Windows."""
    candidates = glob.glob(r"C:\Program Files\Adobe\Adobe After Effects*\Support Files\AfterFX.exe") + \
                 glob.glob(r"D:\*\Adobe\Adobe After Effects*\Support Files\AfterFX.exe")
    if candidates:
        return candidates[0]
    return None

def find_premiere_pro_exe():
    """Look for Adobe Premiere Pro.exe on Windows."""
    candidates = glob.glob(r"C:\Program Files\Adobe\Adobe Premiere Pro*\Adobe Premiere Pro.exe") + \
                 glob.glob(r"D:\*\Adobe\Adobe Premiere Pro*\Adobe Premiere Pro.exe")
    if candidates:
        return candidates[0]
    return None

def execute_bridge_call(fn, args=None):
    """Execute any tool call on the live After Effects CEP Bridge (Port 7788)."""
    token = get_bridge_token()
    url = f"http://{DEFAULT_HOST}:{DEFAULT_PORT}/call"
    body = json.dumps({"fn": fn, "args": args or {}}).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "X-AE-Bridge-Token": token or "test"
    }
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {"ok": True, "data": data}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def check_bridge_connection():
    """Check if the AE / Premiere Pro MCP Bridge CEP panel is open and listening."""
    token = get_bridge_token()
    panel_installed = is_panel_installed()
    mcp_present = os.path.exists(AE_MCP_DIR)
    
    bridge_res = execute_bridge_call("project_info", {})
    ae_exe = find_after_effects_exe()
    ppro_exe = find_premiere_pro_exe()
    
    if bridge_res.get("ok"):
        return {
            "online": True,
            "port": DEFAULT_PORT,
            "mcp_repo_present": mcp_present,
            "panel_installed": panel_installed,
            "project_info": bridge_res["data"].get("result", {}),
            "token_configured": bool(token),
            "ae_installed": bool(ae_exe),
            "ae_path": ae_exe or "Not installed",
            "premiere_installed": bool(ppro_exe),
            "premiere_path": ppro_exe or "Not installed",
            "message": "Adobe MCP Bridge is actively connected on port 7788!"
        }
    
    return {
        "online": False,
        "port": DEFAULT_PORT,
        "mcp_repo_present": mcp_present,
        "panel_installed": panel_installed,
        "error": bridge_res.get("error"),
        "ae_installed": bool(ae_exe),
        "ae_path": ae_exe or "Not found in standard Adobe directory",
        "premiere_installed": bool(ppro_exe),
        "premiere_path": ppro_exe or "Not found in standard Adobe directory",
        "message": "Extension com.aemcpbridge is installed in Adobe CEP. Launch Premiere Pro or After Effects and go to: Window > Extensions > AE MCP Bridge to start live bridge."
    }

def generate_extendscript_with_ai(prompt, comp_type="9:16"):
    """
    Use Gemini AI to turn a natural language motion request into production ExtendScript (.jsx).
    """
    load_env()
    api_key = os.environ.get("GEMINI_API_KEY")

    dim = {"width": 1080, "height": 1920} if comp_type == "9:16" else ({"width": 1920, "height": 1080} if comp_type == "16:9" else {"width": 1080, "height": 1080})

    system_instruction = f"""You are a master Adobe After Effects ExtendScript (JSX) engineer.
Write a clean, bug-free ExtendScript snippet that creates or manipulates a composition in Adobe After Effects.

Composition Specs:
- Dimensions: {dim['width']}x{dim['height']}
- Duration: 15.0 seconds
- Frame Rate: 30 fps

User Request:
"{prompt}"

Rules:
1. Wrap everything in app.beginUndoGroup("ARIS AI Edit") and app.endUndoGroup().
2. If creating a new comp: var comp = app.project.items.addComp("ARIS AI Comp", {dim['width']}, {dim['height']}, 1, 15, 30);
3. Create text layers or solid layers as requested, set source text, position, scale, opacity.
4. Add smooth easing if keyframes are created (e.g. keyInTemporalEase, keyOutTemporalEase).
5. Output ONLY a JSON object with:
{{
  "title": "Short title",
  "explanation": "Friendly explanation of the After Effects animation",
  "jsx_code": "The raw ExtendScript code as a string",
  "comp_name": "ARIS AI Comp"
}}
"""

    if not api_key:
        return fallback_jsx_generator(prompt, comp_type, dim)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": system_instruction}]}],
        "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            return json.loads(raw)
    except Exception as e:
        print(f"[!] Gemini AE planner notice: {e}, using fallback.", file=sys.stderr)
        return fallback_jsx_generator(prompt, comp_type, dim)

def fallback_jsx_generator(prompt, comp_type, dim):
    title = "ARIS Viral Motion Comp"
    code = f"""// ARIS Studio AI - After Effects Auto-Generated ExtendScript
app.beginUndoGroup("ARIS AI Motion Comp");

var project = app.project || app.newProject();
var comp = project.items.addComp("ARIS_Short_{int(datetime.utcnow().timestamp())}", {dim['width']}, {dim['height']}, 1, 15, 30);

// Add Dark Ambient Solid Background
var bg = comp.layers.addSolid([0.05, 0.07, 0.12], "Dark Background", {dim['width']}, {dim['height']}, 1);

// Add Text Layer
var textLayer = comp.layers.addText("{prompt.replace('"', '')[:40]}");
var textProp = textLayer.property("Source Text");
var textDoc = textProp.value;
textDoc.fontSize = 72;
textDoc.fillColor = [1, 1, 1];
textDoc.justification = ParagraphJustification.CENTER_JUSTIFY;
textProp.setValue(textDoc);

// Center and Animate Scale Bounce
var pos = textLayer.property("Transform").property("Position");
pos.setValue([{dim['width']/2}, {dim['height']/2}]);

var scale = textLayer.property("Transform").property("Scale");
scale.setValueAtTime(0.0, [0, 0, 100]);
scale.setValueAtTime(0.5, [115, 115, 100]);
scale.setValueAtTime(0.8, [100, 100, 100]);

app.endUndoGroup();
"""
    return {
        "title": title,
        "explanation": f"Generated an After Effects {comp_type} composition with dark ambient backdrop and scale-bounce animated text.",
        "jsx_code": code,
        "comp_name": "ARIS AI Comp"
    }

def save_and_dispatch_jsx(jsx_code, comp_name="ARIS_Comp"):
    """
    Saves the .jsx file to data/ae_scripts/ and sends it to After Effects if bridge is live.
    """
    os.makedirs(AE_SCRIPTS_DIR, exist_ok=True)
    ts = int(datetime.utcnow().timestamp())
    filename = f"ae_script_{ts}.jsx"
    file_path = os.path.join(AE_SCRIPTS_DIR, filename)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(jsx_code)

    bridge_status = check_bridge_connection()
    dispatched = False
    bridge_result = None

    if bridge_status.get("online"):
        run_res = execute_bridge_call("run_jsx", {"code": jsx_code})
        if run_res.get("ok"):
            bridge_result = run_res["data"]
            dispatched = True
        else:
            bridge_result = run_res

    return {
        "success": True,
        "file_path": file_path,
        "filename": filename,
        "dispatched_to_ae_live": dispatched,
        "bridge_status": bridge_status,
        "bridge_result": bridge_result,
        "how_to_use": "If After Effects is open, you can run this script live, or open After Effects and go to: File > Scripts > Run Script File... and choose this .jsx file."
    }

if __name__ == "__main__":
    status = check_bridge_connection()
    print("Bridge Status:", json.dumps(status, indent=2))
