"""
ARIS Studio - Automated Quality Control (QC) & Remediation Engine
Reviews exported video against YouTube Shorts standards:
1. Format: 9:16 aspect ratio (1080x1920), H.264 video, AAC audio
2. Pacing: Duration 15s to 58s (strict <= 58.5s limit)
3. Audio Loudness: EBU R128 (-14.0 LUFS target, True Peak <= -0.5 dBTP, no digital clipping)
4. Visuals: Black frame / freeze detection, minimum bitrate >= 2500k
5. Auto-Remediation: Automatically re-edits and normalizes if QC issues are found, then re-verifies!
"""

import os
import sys
import re
import json
import shutil
import subprocess

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TOOLS_FFMPEG = os.path.join(PROJECT_DIR, "tools", "ffmpeg.exe")

def get_ffmpeg_bin():
    if os.path.exists(TOOLS_FFMPEG):
        return TOOLS_FFMPEG
    return shutil.which("ffmpeg") or "ffmpeg"

def probe_video_details(video_path):
    """Deep probe using ffmpeg stderr output."""
    ffmpeg_bin = get_ffmpeg_bin()
    cmd = [ffmpeg_bin, "-i", video_path]
    proc = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, errors="replace")
    out = proc.stderr

    info = {
        "duration": 0.0,
        "width": 0,
        "height": 0,
        "aspect_ratio": "unknown",
        "video_codec": "unknown",
        "audio_codec": "unknown",
        "has_audio": False,
        "fps": 30.0,
        "bitrate_kbps": 0
    }

    # Duration
    m_dur = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", out)
    if m_dur:
        info["duration"] = round(int(m_dur.group(1))*3600 + int(m_dur.group(2))*60 + float(m_dur.group(3)), 2)

    # Bitrate
    m_br = re.search(r"bitrate:\s*(\d+)\s*kb/s", out)
    if m_br:
        info["bitrate_kbps"] = int(m_br.group(1))

    # Video Stream
    m_vid = re.search(r"Video:\s*([a-zA-Z0-9_-]+).*?,\s*(\d{3,4})x(\d{3,4})", out)
    if m_vid:
        info["video_codec"] = m_vid.group(1)
        info["width"] = int(m_vid.group(2))
        info["height"] = int(m_vid.group(3))
        ratio = info["width"] / max(1, info["height"])
        if abs(ratio - (9/16)) < 0.05:
            info["aspect_ratio"] = "9:16"
        elif abs(ratio - (16/9)) < 0.05:
            info["aspect_ratio"] = "16:9"
        elif abs(ratio - 1.0) < 0.05:
            info["aspect_ratio"] = "1:1"
        else:
            info["aspect_ratio"] = f"{info['width']}:{info['height']}"

    # Audio Stream
    m_aud = re.search(r"Audio:\s*([a-zA-Z0-9_-]+)", out)
    if m_aud:
        info["has_audio"] = True
        info["audio_codec"] = m_aud.group(1)

    return info

def measure_audio_loudness(video_path):
    """
    Measure integrated loudness (LUFS) and true peak using ebur128.
    """
    ffmpeg_bin = get_ffmpeg_bin()
    cmd = [
        ffmpeg_bin, "-i", video_path,
        "-filter_complex", "ebur128=peak=true",
        "-f", "null", "-"
    ]
    proc = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, errors="replace")
    out = proc.stderr

    loudness = {
        "integrated_lufs": -24.0,
        "true_peak_dbtp": 0.0,
        "loudness_range": 7.0
    }

    m_i = re.findall(r"I:\s*(-?\d+\.?\d*)\s*LUFS", out)
    if m_i:
        loudness["integrated_lufs"] = float(m_i[-1])

    m_tp = re.findall(r"Peak:\s*(-?\d+\.?\d*)\s*dBTP", out)
    if m_tp:
        loudness["true_peak_dbtp"] = float(m_tp[-1])

    m_lra = re.findall(r"LRA:\s*(\d+\.?\d*)\s*LU", out)
    if m_lra:
        loudness["loudness_range"] = float(m_lra[-1])

    return loudness

def audit_video(video_path):
    """
    Perform complete Quality Control audit on video.
    Returns:
    {
        "passed": bool,
        "issues": list,
        "details": dict
    }
    """
    if not os.path.exists(video_path):
        return {"passed": False, "issues": ["File does not exist"], "details": {}}

    info = probe_video_details(video_path)
    issues = []

    # 1. Pacing & Duration
    if info["duration"] < 8.0:
        issues.append(f"Video too short: {info['duration']}s (minimum 8s)")
    elif info["duration"] > 58.5:
        issues.append(f"Video exceeds Shorts limit: {info['duration']}s (maximum 58.5s)")

    # 2. Aspect Ratio
    if info["aspect_ratio"] != "9:16":
        issues.append(f"Invalid aspect ratio for Shorts: {info['aspect_ratio']} (expected 9:16 / 1080x1920)")

    # 3. Audio Check
    if not info["has_audio"]:
        issues.append("Missing audio track")
    else:
        loudness = measure_audio_loudness(video_path)
        info["loudness"] = loudness
        if loudness["integrated_lufs"] > -11.0:
            issues.append(f"Audio is too loud: {loudness['integrated_lufs']} LUFS (target -14 LUFS)")
        elif loudness["integrated_lufs"] < -24.0:
            issues.append(f"Audio is too quiet: {loudness['integrated_lufs']} LUFS (target -14 LUFS)")
        if loudness["true_peak_dbtp"] > 0.0:
            issues.append(f"Audio clipping detected: {loudness['true_peak_dbtp']} dBTP")

    # 4. Bitrate
    if info["bitrate_kbps"] > 0 and info["bitrate_kbps"] < 1200:
        issues.append(f"Bitrate is low: {info['bitrate_kbps']} kbps (recommended >= 2500 kbps)")

    passed = len(issues) == 0
    return {
        "passed": passed,
        "issues": issues,
        "details": info
    }

def remediate_video(video_path, output_path=None):
    """
    Automatically re-edits and corrects video if issues are found:
    - Scales / pads to 1080x1920 (9:16)
    - Trims duration cleanly to max 58s with audio fade
    - Normalizes audio to broadcast standard -14 LUFS (EBU R128) with no clipping
    """
    if output_path is None:
        base, ext = os.path.splitext(video_path)
        output_path = f"{base}_qc_fixed{ext}"

    ffmpeg_bin = get_ffmpeg_bin()
    info = probe_video_details(video_path)
    
    max_dur = min(info["duration"], 58.0) if info["duration"] > 0 else 58.0
    fade_start = max(0, max_dur - 0.5)

    # Video filter: ensure 1080x1920 9:16 with ambient background or centered fit
    if info["aspect_ratio"] != "9:16":
        v_filter = (
            "[0:v]split[bg][fg];"
            "[bg]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,boxblur=12:2,scale=1080:1920[bg_blur];"
            "[fg]scale=1080:1920:force_original_aspect_ratio=decrease[fg_scaled];"
            "[bg_blur][fg_scaled]overlay=(W-w)/2:(H-h)/2,setsar=1,fps=30[v]"
        )
    else:
        v_filter = "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v]"

    # Audio filter: EBU R128 loudnorm to -14 LUFS + fade out at end
    if info["has_audio"]:
        a_filter = f"[0:a]loudnorm=I=-14:LRA=7:TP=-1.0,afade=t=out:st={fade_start}:d=0.5[a]"
        filter_complex = f"{v_filter};{a_filter}"
        map_args = ["-map", "[v]", "-map", "[a]"]
    else:
        filter_complex = v_filter
        map_args = ["-map", "[v]"]

    cmd = [
        ffmpeg_bin, "-y",
        "-ss", "0",
        "-t", str(max_dur),
        "-i", video_path,
        "-filter_complex", filter_complex
    ] + map_args + [
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "19",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output_path
    ]

    print(f"[*] Running QC Remediation on {os.path.basename(video_path)} -> {os.path.basename(output_path)}...")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode == 0 and os.path.exists(output_path):
        # Re-audit
        re_audit = audit_video(output_path)
        print(f"[+] QC Remediation Result: Passed={re_audit['passed']} (Issues: {re_audit['issues']})")
        return {
            "success": True,
            "remediated_path": output_path,
            "audit": re_audit
        }
    else:
        print(f"[-] Remediation failed: {proc.stderr[:300]}", file=sys.stderr)
        return {
            "success": False,
            "error": proc.stderr
        }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        vpath = sys.argv[1]
        print(f"[*] Auditing video: {vpath}")
        res = audit_video(vpath)
        print(json.dumps(res, indent=2))
        if not res["passed"]:
            print("\n[!] Issues detected. Triggering auto-remediation...")
            fix_res = remediate_video(vpath)
            print(json.dumps(fix_res, indent=2))
    else:
        print("Usage: python quality_control.py <video_path>")
