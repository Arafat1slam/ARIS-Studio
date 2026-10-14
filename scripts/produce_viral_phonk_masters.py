"""
ARIS Studio - Viral Phonk Master Video Engine
Produces 2 Ultra-High Retention Videos using Authentic Viral Phonk Anthems:
1. Video 1: "AKAZA: CRIMSON MOON" - 60FPS Velocity Anime AMV powered by Viral Brazilian Phonk (Montagem Diamante Rosa)
2. Video 2: "DARK PSYCHOLOGY: POWER OF SILENCE" - Fight Club Noir Master powered by DVRST Close Eyes (Slowed + Reverb) + Christopher Studio Voiceover

Delivers:
- Ready-to-Publish 1080x1920 9:16 MP4s in data/processed_shorts/ and C:\\Users\\ARIS EN\\Downloads
- Full Adobe Premiere Pro 2026 XML Sequences & ExtendScript JSX
- Full Adobe After Effects Pro Master Compositions
"""

import os
import sys
import glob
import shutil
import asyncio
import subprocess
import re

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from datetime import datetime, timezone

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(PROJECT_DIR)
sys.path.append(os.path.join(PROJECT_DIR, "scripts"))

import quality_control
import edge_tts
import premiere_automation
import aftereffects_bridge

FFMPEG = r"tools\ffmpeg.exe" if os.path.exists(r"tools\ffmpeg.exe") else "ffmpeg"
BROLL_DIR = os.path.join(PROJECT_DIR, "data", "broll", "scenepacks")
BGM_DIR = os.path.join(PROJECT_DIR, "data", "bgm")
OUT_DIR = os.path.join(PROJECT_DIR, "data", "processed_shorts")
TEMP_DIR = os.path.join(PROJECT_DIR, "data", "temp")
DOWNLOADS_DIR = os.path.expanduser("~\\Downloads")

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

def safe_copy_to_downloads(src_path, filename_base):
    dest = os.path.join(DOWNLOADS_DIR, f"{filename_base}.mp4")
    try:
        shutil.copyfile(src_path, dest)
        return dest
    except PermissionError:
        ts = int(datetime.now(timezone.utc).timestamp())
        alt_dest = os.path.join(DOWNLOADS_DIR, f"{filename_base}_{ts}.mp4")
        shutil.copyfile(src_path, alt_dest)
        return alt_dest

def produce_video1_viral_brazilian_phonk_amv():
    """
    Video 1: eitaX Standard Akaza 60FPS Velocity AMV
    Song: Viral Montagem Diamante Rosa (Brazilian Phonk - Ultra Bass)
    """
    print("\n" + "="*75)
    print("🩸 VIDEO 1: PRODUCING VIRAL BRAZILIAN PHONK ANIME AMV (AKAZA 60FPS)")
    print("   Track: Montagem Diamante Rosa (Slowed 808 Bass Boost)")
    print("="*75)

    # 1. Source 8 Akaza Shots
    akaza_clips = sorted(glob.glob(os.path.join(BROLL_DIR, "akaza_action_*.mp4")))
    if not akaza_clips or len(akaza_clips) < 6:
        raise RuntimeError("Akaza clips not found in data/broll/scenepacks.")

    selected_clips = akaza_clips[:8]
    total_dur = 17.5 # 17.5 seconds sweet spot
    dur_per_shot = total_dur / len(selected_clips) # ~2.18s

    # 2. Master Viral Brazilian Phonk (Slowed + 808 Sub-Bass Boost)
    phonk_raw = os.path.join(BGM_DIR, "viral_montagem_diamante_rosa.mp3")
    if not os.path.exists(phonk_raw):
        phonk_raw = os.path.join(BGM_DIR, "aggressive_drift_phonk.mp3")

    phonk_mastered = os.path.join(TEMP_DIR, "v1_brazilian_phonk_master.mp3")
    # Cut to length, tempo 0.94x, heavy 808 sub-bass (+7dB @ 60Hz), high-end sizzle, -14 LUFS
    audio_cmd = [
        FFMPEG, "-y",
        "-ss", "00:00:08",
        "-i", phonk_raw,
        "-t", str(total_dur),
        "-filter_complex",
        "atempo=0.94,equalizer=f=60:width_type=h:width=45:g=7.0,equalizer=f=3800:width_type=h:width=900:g=3.0,aecho=0.8:0.7:25:0.3,loudnorm=I=-14:LRA=7:TP=-1.0",
        "-c:a", "libmp3lame", "-b:a", "320k",
        phonk_mastered
    ]
    subprocess.run(audio_cmd, check=True, capture_output=True)
    print("[+] Audio Mastered: Viral Brazilian Phonk 808 Boost (-14 LUFS)")

    # 3. ASS Kinetic Subtitles (Stomp on Beat)
    ass_path = os.path.join(TEMP_DIR, "v1_kinetic_subs.ass")
    ass_header = """[Script Info]
Title: Akaza Viral Phonk AMV
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TitleBadge,Impact,48,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,3,0,1,6,2,8,40,40,240,1
Style: HookGold,Impact,92,&H002BF7FF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,105,105,2,0,1,9,5,5,40,40,960,1
Style: HookCrimson,Impact,96,&H003333FF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,110,110,2,0,1,10,6,5,40,40,960,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:17.50,TitleBadge,,0,0,0,,{\\an8\\bord5\\shad2\\c&H003333FF&}⚡ AKAZA • UPPER MOON THREE ⚡
Dialogue: 1,0:00:00.00,0:00:02.18,HookGold,,0,0,0,,{\\t(0,250,\\fscx140\\fscy140)\\t(250,500,\\fscx100\\fscy100)}BECOME A DEMON
Dialogue: 1,0:00:02.18,0:00:04.36,HookCrimson,,0,0,0,,{\\t(0,250,\\fscx140\\fscy140)\\t(250,500,\\fscx100\\fscy100)}OR DIE AS A WEAKLING
Dialogue: 1,0:00:04.36,0:00:06.54,HookGold,,0,0,0,,{\\t(0,250,\\fscx140\\fscy140)\\t(250,500,\\fscx100\\fscy100)}COMPASS NEEDLE
Dialogue: 1,0:00:06.54,0:00:08.72,HookCrimson,,0,0,0,,{\\t(0,250,\\fscx140\\fscy140)\\t(250,500,\\fscx100\\fscy100)}DESTRUCTIVE DEATH
Dialogue: 1,0:00:08.72,0:00:10.90,HookGold,,0,0,0,,{\\t(0,250,\\fscx140\\fscy140)\\t(250,500,\\fscx100\\fscy100)}SUPREME TERRITORY
Dialogue: 1,0:00:10.90,0:00:13.08,HookCrimson,,0,0,0,,{\\t(0,250,\\fscx140\\fscy140)\\t(250,500,\\fscx100\\fscy100)}LIMITLESS POWER
Dialogue: 1,0:00:13.08,0:00:15.26,HookGold,,0,0,0,,{\\t(0,250,\\fscx140\\fscy140)\\t(250,500,\\fscx100\\fscy100)}NO REGRETS
Dialogue: 1,0:00:15.26,0:00:17.50,HookCrimson,,0,0,0,,{\\t(0,250,\\fscx140\\fscy140)\\t(250,500,\\fscx100\\fscy100)}CRIMSON MOON
"""
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header)

    # 4. Render Velocity 60FPS Shots
    rendered_shots = []
    for idx, clip in enumerate(selected_clips):
        shot_path = os.path.join(TEMP_DIR, f"v1_velocity_{idx:02d}.mp4")
        vf = (
            "scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,"
            "scale='1080*(1+0.09*exp(-9*t))':'1920*(1+0.09*exp(-9*t))':eval=frame,"
            "crop=1080:1920,"
            "rgbashift=rh=5:bv=-5:edge=smear,"
            "fade=t=in:st=0:d=0.06:color=white,"
            "eq=contrast=1.35:saturation=1.40:brightness=-0.02,"
            "unsharp=5:5:1.1:5:5:0.0,"
            "fps=60"
        )
        cmd = [
            FFMPEG, "-y",
            "-i", clip,
            "-t", str(dur_per_shot),
            "-vf", vf,
            "-c:v", "libx264", "-preset", "fast", "-crf", "16",
            "-an",
            shot_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        rendered_shots.append(shot_path)
        print(f" [+] Rendered 60FPS Velocity Shot {idx+1}/{len(selected_clips)}")

    # Concat Shots
    concat_file = os.path.join(TEMP_DIR, "v1_concat.txt")
    with open(concat_file, "w", encoding="utf-8") as f:
        for p in rendered_shots:
            f.write(f"file '{p.replace(os.sep, '/')}'\n")

    # 5. Master Composite
    ass_escaped = ass_path.replace("\\", "/").replace(":", "\\:")
    filter_complex = (
        f"[0:v]subtitles='{ass_escaped}',"
        "split[base][glow_in];"
        "[glow_in]boxblur=18:2,eq=brightness=0.12:contrast=1.35[glow_soft];"
        "[base][glow_soft]blend=all_mode=screen:all_opacity=0.32,"
        "fps=60[v]"
    )

    out_file = os.path.join(OUT_DIR, "Channel1_Viral_Phonk_Akaza_60FPS.mp4")
    cmd_master = [
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0", "-i", concat_file,
        "-i", phonk_mastered,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", "1:a",
        "-c:v", "libx264", "-preset", "slow", "-crf", "16",
        "-c:a", "aac", "-b:a", "320k",
        "-movflags", "+faststart",
        out_file
    ]
    subprocess.run(cmd_master, check=True, capture_output=True)
    print(f"[OK] Master Video 1 Rendered: {os.path.basename(out_file)} ({os.path.getsize(out_file)/(1024*1024):.2f} MB)")

    # 6. Generate Premiere Pro XML & JSX + After Effects Pro Comp
    ppro_res = premiere_automation.build_pro_editing_package(selected_clips, bgm_path=phonk_mastered, title="Akaza_Viral_Brazilian_Phonk_60FPS")
    ae_res = aftereffects_bridge.generate_pro_aftereffects_comp(selected_clips, words=["BECOME", "DEMON", "UPPER", "THREE", "CRIMSON"], bgm_path=phonk_mastered, title="Akaza_Viral_Brazilian_Phonk_60FPS")
    print(f"🎬 Premiere Pro XML: {ppro_res['xml']['xml_path']}")
    print(f"🎬 Premiere Pro JSX: {ppro_res['jsx']['script_path']}")
    print(f"🎬 After Effects JSX: {ae_res['file_path']}")

    # 7. Copy directly to Downloads
    dst = safe_copy_to_downloads(out_file, "Channel1_Viral_Phonk_Akaza_60FPS")
    print(f"🎉 EXPORTED TO DOWNLOADS: {dst} ({os.path.getsize(dst)/(1024*1024):.2f} MB)")
    return dst


def produce_video2_viral_phonk_dark_psychology():
    """
    Video 2: Fight Club Noir Dark Psychology Master
    Song: DVRST - Close Eyes (Viral Slowed + Reverb Phonk Anthem)
    Voiceover: Microsoft Edge-TTS ChristopherNeural (Deep Stoic Studio Audio)
    """
    print("\n" + "="*75)
    print("🧠 VIDEO 2: PRODUCING VIRAL PHONK DARK PSYCHOLOGY SHORT (FIGHT CLUB)")
    print("   Track: DVRST - Close Eyes (Slowed + Reverb) + Christopher Studio VO")
    print("="*75)

    # 1. Studio Voiceover
    script_lines = [
        ("Rule number one: Never react immediately.", "Red"),
        ("When someone disrespects you in public...", "Normal"),
        ("Stare into their eyes in dead silence for two seconds.", "Gold"),
        ("Then ask calmly: 'Are you feeling okay?'", "Gold"),
        ("In that single second, their power collapses.", "Normal"),
        ("While they panic to fill the silence...", "Normal"),
        ("You control the entire room.", "Gold"),
        ("Silence is not weakness...", "Normal"),
        ("It is psychological dominance.", "Red")
    ]

    vo_path = os.path.join(TEMP_DIR, "v2_vo_christopher_phonk.mp3")
    full_text = " ".join([l[0] for l in script_lines])

    print("[*] Generating studio voiceover via Microsoft Christopher Neural...")
    async def run_edge():
        comm = edge_tts.Communicate(full_text, voice="en-US-ChristopherNeural", rate="-3%", pitch="-2Hz")
        await comm.save(vo_path)
    asyncio.run(run_edge())
    print("[+] Voiceover Generated: en-US-ChristopherNeural")

    # Probe duration
    proc = subprocess.run([FFMPEG, "-i", vo_path], capture_output=True, text=True)
    total_dur = 23.5
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", proc.stderr)
    if m:
        total_dur = int(m.group(1))*3600 + int(m.group(2))*60 + float(m.group(3))
    print(f"[+] Voiceover Duration: {total_dur:.2f}s")

    # 2. Master Viral Phonk BGM (DVRST Close Eyes)
    bgm_raw = os.path.join(BGM_DIR, "viral_dvrst_close_eyes_slowed.mp3")
    if not os.path.exists(bgm_raw):
        bgm_raw = os.path.join(BGM_DIR, "viral_dxrk_rave_slowed.mp3")

    bgm_mastered = os.path.join(TEMP_DIR, "v2_dvrst_phonk_master.mp3")
    audio_cmd = [
        FFMPEG, "-y",
        "-ss", "00:00:12",
        "-i", bgm_raw,
        "-t", str(total_dur + 1.0),
        "-filter_complex",
        "equalizer=f=60:width_type=h:width=40:g=6.0,equalizer=f=3500:width_type=h:width=800:g=2.5,aecho=0.8:0.7:30:0.35,loudnorm=I=-14:LRA=7:TP=-1.0",
        "-c:a", "libmp3lame", "-b:a", "320k",
        bgm_mastered
    ]
    subprocess.run(audio_cmd, check=True, capture_output=True)
    print("[+] BGM Mastered: DVRST Close Eyes Slowed Phonk")

    # 3. ASS Subtitles
    ass_path = os.path.join(TEMP_DIR, "v2_subs_phonk_dark.ass")
    step = total_dur / len(script_lines)
    cues = [(i * step, (i + 1) * step, l[0]) for i, l in enumerate(script_lines)]

    header = f"""[Script Info]
Title: Dark Psychology Phonk
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Badge,Impact,46,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,3,0,1,6,2,8,40,40,240,1
Style: SubNormal,Arial Black,68,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,8,4,5,60,60,960,1
Style: SubGold,Arial Black,74,&H002BF7FF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,104,104,2,0,1,10,5,5,60,60,960,1
Style: SubRed,Arial Black,76,&H003333FF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,106,106,2,0,1,10,5,5,60,60,960,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:{int(total_dur//60):02d}:{total_dur%60:05.2f},Badge,,0,0,0,,{{\\an8\\bord4\\shad1\\c&H003333FF&}}⚠️ THE POWER OF SILENCE ⚠️
"""
    events = []
    for idx, cue in enumerate(cues):
        st = f"0:{int(cue[0]//60):02d}:{cue[0]%60:05.2f}"
        et = f"0:{int(cue[1]//60):02d}:{cue[1]%60:05.2f}"
        c_pref = script_lines[idx][1]
        style = "SubGold" if c_pref == "Gold" else ("SubRed" if c_pref == "Red" else "SubNormal")
        events.append(f"Dialogue: 1,{st},{et},{style},,0,0,0,,{cue[2].upper()}")

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(events))

    # 4. Process Fight Club 1080p REMUX Shots with Slow Push-In & Noir Contrast Grade
    fc_clips = sorted(glob.glob(os.path.join(BROLL_DIR, "fight_club_scene_*.mp4")))[:8]
    dur_per_shot = (total_dur + 0.8) / len(fc_clips)
    rendered_fc = []

    for idx, cp in enumerate(fc_clips):
        shot_out = os.path.join(TEMP_DIR, f"v2_fc_shot_{idx:02d}.mp4")
        vf = (
            "scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,"
            "scale='1080*(1+0.05*t)':'1920*(1+0.05*t)':eval=frame,"
            "crop=1080:1920,"
            "eq=contrast=1.35:saturation=0.82:brightness=-0.03,"
            "vignette=PI/4.3,"
            "fade=t=in:st=0:d=0.08:color=black,"
            "fps=30"
        )
        cmd = [
            FFMPEG, "-y",
            "-i", cp,
            "-t", str(dur_per_shot),
            "-vf", vf,
            "-c:v", "libx264", "-preset", "fast", "-crf", "17",
            "-an",
            shot_out
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        rendered_fc.append(shot_out)
        print(f" [+] Rendered Noir Push-In Scene {idx+1}/{len(fc_clips)}")

    concat_file = os.path.join(TEMP_DIR, "v2_fc_concat.txt")
    with open(concat_file, "w", encoding="utf-8") as f:
        for p in rendered_fc:
            f.write(f"file '{p.replace(os.sep, '/')}'\n")

    # 5. Master Composite: Voiceover + Ducked Phonk BGM + Subtitles
    ass_escaped = ass_path.replace("\\", "/").replace(":", "\\:")
    filter_complex = (
        f"[0:v]subtitles='{ass_escaped}',fps=30[v];"
        f"[1:a]volume=1.0[vo];"
        f"[2:a]atrim=0:{total_dur + 0.8},volume=0.22,afade=t=out:st={total_dur}:d=0.8[bgm];"
        f"[vo][bgm]amix=inputs=2:duration=first:dropout_transition=2,"
        f"loudnorm=I=-14:LRA=7:TP=-1.0[a]"
    )

    out_file = os.path.join(OUT_DIR, "Channel2_Viral_Phonk_DarkPsychology.mp4")
    cmd_master = [
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0", "-i", concat_file,
        "-i", vo_path,
        "-i", bgm_mastered,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", "[a]",
        "-c:v", "libx264", "-preset", "slow", "-crf", "16",
        "-c:a", "aac", "-b:a", "320k",
        "-movflags", "+faststart",
        out_file
    ]
    subprocess.run(cmd_master, check=True, capture_output=True)
    print(f"[OK] Master Video 2 Rendered: {os.path.basename(out_file)} ({os.path.getsize(out_file)/(1024*1024):.2f} MB)")

    # 6. Generate Premiere Pro XML & JSX + After Effects Pro Comp
    ppro_res = premiere_automation.build_pro_editing_package(fc_clips, voiceover_path=vo_path, bgm_path=bgm_mastered, title="DarkPsychology_PowerOfSilence_Phonk")
    ae_res = aftereffects_bridge.generate_pro_aftereffects_comp(fc_clips, words=["NEVER", "REACT", "MASTER", "THE", "SILENCE"], bgm_path=bgm_mastered, title="DarkPsychology_PowerOfSilence_Phonk")
    print(f"🎬 Premiere Pro XML: {ppro_res['xml']['xml_path']}")
    print(f"🎬 Premiere Pro JSX: {ppro_res['jsx']['script_path']}")
    print(f"🎬 After Effects JSX: {ae_res['file_path']}")

    # 7. Copy directly to Downloads
    dst = safe_copy_to_downloads(out_file, "Channel2_Viral_Phonk_DarkPsychology")
    print(f"🎉 EXPORTED TO DOWNLOADS: {dst} ({os.path.getsize(dst)/(1024*1024):.2f} MB)")
    return dst


if __name__ == "__main__":
    v1 = produce_video1_viral_brazilian_phonk_amv()
    v2 = produce_video2_viral_phonk_dark_psychology()

    print("\n" + "="*75)
    print("🏆 BOTH MASTER VIDEOS WITH VIRAL PHONK SONGS SUCCESSFULLY GENERATED:")
    print(" 1. Channel 1 (Viral Brazilian Phonk 60FPS Akaza AMV):")
    print("    📍", v1)
    print(" 2. Channel 2 (DVRST Close Eyes Dark Psychology Master):")
    print("    📍", v2)
    print("="*75)
