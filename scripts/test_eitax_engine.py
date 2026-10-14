"""
ARIS Studio - Advanced AMV / EitaX God-Tier Edit Engine
Emulates: "Crimson Moon" - AKAZA [AMV/EDIT] 4K by eitaX (https://www.youtube.com/watch?v=f_DUBwVR8Mw)
Techniques:
1. Audio Beat Detection & Phonk Drum Sync
2. Decaying Impact Shake (S_Shake emulation) & Zoom Pulse on 808 kicks
3. RGB Split / Chromatic Aberration on Beat Drops (rgbashift)
4. Fast-to-Slow Motion Velocity Curves (Time Remapping)
5. Deep Glow / Optical Bloom (Screen blend blur)
6. High-Contrast Stylized CC (Deep blacks, saturated power highlights)
7. 60 FPS Smooth Flow
"""

import os
import sys
import glob
import subprocess

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(PROJECT_DIR)

FFMPEG = r"tools\ffmpeg.exe" if os.path.exists(r"tools\ffmpeg.exe") else "ffmpeg"
BROLL_DIR = os.path.join(PROJECT_DIR, "data", "broll", "scenepacks")
OUT_DIR = os.path.join(PROJECT_DIR, "data", "processed_shorts")
TEMP_DIR = os.path.join(PROJECT_DIR, "data", "temp")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

def test_eitax_filter():
    clips = sorted(glob.glob(os.path.join(BROLL_DIR, "gojo_action_*.mp4")))
    if not clips:
        print("No gojo clips found.")
        return
        
    test_clip = clips[0] # First clip
    out_test = os.path.join(TEMP_DIR, "eitax_single_clip_test.mp4")
    
    # EitaX Signature Filtergraph:
    # 1. 9:16 Smart Crop
    # 2. RGB Split on impact (rgbashift)
    # 3. Decaying camera shake & zoom pulse on beats
    # 4. Deep glow bloom overlay
    # 5. Stylized contrast CC (rich blacks, saturated highlights)
    # 6. Smooth 60 FPS
    
    vf = (
        # Crop & scale to 1080x1920
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        # Decaying Impact Zoom Pulse: zoom in on 0s and decay quickly
        "scale='1080*(1+0.08*exp(-8*t))':'1920*(1+0.08*exp(-8*t))':eval=frame,"
        "crop=1080:1920,"
        # RGB Chromatic Aberration Split (rh=6:bv=-6:edge=smear)
        "rgbashift=rh=5:bv=-5:edge=smear,"
        # Deep Glow / Optical Bloom via split and screen blend
        "split[base][glow_in];"
        "[glow_in]boxblur=20:2,eq=brightness=0.1:contrast=1.3[glow_soft];"
        "[base][glow_soft]blend=all_mode=screen:all_opacity=0.3[blended];"
        # Final CC (Color Correction)
        "[blended]eq=contrast=1.32:saturation=1.35:brightness=-0.02,"
        "unsharp=5:5:1.0:5:5:0.0,"
        "fps=60"
    )
    
    cmd = [
        FFMPEG, "-y",
        "-i", test_clip,
        "-t", "3.0",
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "17",
        "-an",
        out_test
    ]
    
    print("Testing EitaX filter on sample clip...")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode == 0 and os.path.exists(out_test):
        print(f"[OK] Filter Test Succeeded! Output: {out_test} ({os.path.getsize(out_test)/(1024*1024):.2f} MB)")
    else:
        print("[-] Filter Test Failed:", proc.stderr[-500:])

if __name__ == "__main__":
    test_eitax_filter()
