"""
ARIS After Effects Bridge & AI ExtendScript Automation Engine
Integrates features inspired by aftereffects-mcp:
1. Direct connection to running Adobe After Effects instance via CEP Bridge (port 7788).
2. AI-driven ExtendScript (.jsx) generation from natural language prompts.
3. Automated Comp creation (9:16 vertical shorts, 16:9 4K, 1:1 square).
4. Keyframing, text animation, easing presets, and aerender exports.
"""

import os
import sys
import json
import glob
import urllib.request
import urllib.error
from datetime import datetime

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_FILE = os.path.join(PROJECT_DIR, ".env")
AE_SCRIPTS_DIR = os.path.join(PROJECT_DIR, "data", "ae_scripts")
AE_PREVIEWS_DIR = os.path.join(PROJECT_DIR, "data", "ae_previews")

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

def find_after_effects_exe():
    """Look for AfterFX.exe or aerender.exe on Windows."""
    candidates = glob.glob(r"C:\Program Files\Adobe\Adobe After Effects*\Support Files\AfterFX.exe")
    if candidates:
        return candidates[0]
    return None

def check_bridge_connection():
    """Check if the AE MCP Bridge CEP panel is open and listening."""
    token = get_bridge_token()
    url = f"http://{DEFAULT_HOST}:{DEFAULT_PORT}/call"
    test_body = json.dumps({"fn": "project_info", "args": {}}).encode("utf-8")
    
    headers = {
        "Content-Type": "application/json",
        "X-AE-Bridge-Token": token or "test"
    }

    req = urllib.request.Request(url, data=test_body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {
                "online": True,
                "port": DEFAULT_PORT,
                "project_info": data.get("result", {}),
                "token_configured": bool(token)
            }
    except Exception as e:
        ae_exe = find_after_effects_exe()
        return {
            "online": False,
            "port": DEFAULT_PORT,
            "error": str(e),
            "ae_installed": bool(ae_exe),
            "ae_path": ae_exe or "Not found in standard Adobe directory",
            "message": "After Effects is not currently running with the AE MCP Bridge panel open. ExtendScript (.jsx) generator will operate in standalone file mode."
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
        token = get_bridge_token()
        url = f"http://{DEFAULT_HOST}:{DEFAULT_PORT}/call"
        body = json.dumps({"fn": "run_jsx", "args": {"code": jsx_code}}).encode("utf-8")
        headers = {"Content-Type": "application/json", "X-AE-Bridge-Token": token}
        try:
            req = urllib.request.Request(url, data=body, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                bridge_result = json.loads(resp.read().decode("utf-8"))
                dispatched = True
        except Exception as be:
            bridge_result = {"error": str(be)}

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
    plan = generate_extendscript_with_ai("Make 9:16 dark psychology kinetic typography intro", "9:16")
    res = save_and_dispatch_jsx(plan["jsx_code"])
    print("Result:", json.dumps(res, indent=2))
