#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess, sys
from pathlib import Path

PROFILES = {
    "MOBILE_SAVER_480P": {"scale": "854:480", "maxrate": "700k", "bufsize": "1400k", "audio": "64k"},
    "MOBILE_720P": {"scale": "1280:720", "maxrate": "1800k", "bufsize": "3600k", "audio": "96k"},
    "STANDARD_1080P": {"scale": "1920:1080", "maxrate": "4000k", "bufsize": "8000k", "audio": "128k"},
}

def run(cmd):
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def probe(path):
    p = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)])
    if p.returncode:
        raise RuntimeError(p.stderr.strip() or "ffprobe failed")
    return json.loads(p.stdout)

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def duration(meta):
    return float(meta.get("format", {}).get("duration", 0) or 0)

def streams(meta, kind):
    return [s for s in meta.get("streams", []) if s.get("codec_type") == kind]

def validate(master_meta, output_meta, cfg):
    md, od = duration(master_meta), duration(output_meta)
    if od <= 0 or abs(od - md) > 0.250:
        raise RuntimeError(f"duration gate failed: {md:.3f}s -> {od:.3f}s")
    vs = streams(output_meta, "video")
    if not vs:
        raise RuntimeError("missing video stream")
    src = streams(master_meta, "video")
    if src:
        sw, sh = int(src[0].get("width") or 0), int(src[0].get("height") or 0)
        ow, oh = int(vs[0].get("width") or 0), int(vs[0].get("height") or 0)
        tw, th = map(int, cfg["scale"].split(":"))
        if ow > tw or oh > th:
            raise RuntimeError(f"dimension gate failed: {ow}x{oh}")
        if ow > sw or oh > sh:
            raise RuntimeError(f"upscale gate failed: source={sw}x{sh}, output={ow}x{oh}")
    ma, oa = streams(master_meta, "audio"), streams(output_meta, "audio")
    if ma and not oa:
        raise RuntimeError("master has audio but output has none")
    if oa and abs(float(oa[0].get("duration") or od) - od) > 0.250:
        raise RuntimeError("audio/video timing gate failed")
    ms, os = streams(master_meta, "subtitle"), streams(output_meta, "subtitle")
    if ms and len(os) != len(ms):
        raise RuntimeError(f"subtitle count gate failed: {len(os)} != {len(ms)}")

def transcode(master, out, cfg):
    out.parent.mkdir(parents=True, exist_ok=True)
    tw, th = map(int, cfg["scale"].split(":"))
    scale_filter = f"scale=w='min(iw,{tw})':h='min(ih,{th})':force_original_aspect_ratio=decrease:force_divisible_by=2"
    cmd = [
        "ffmpeg", "-y", "-i", str(master),
        "-map", "0:v:0", "-map", "0:a?", "-map", "0:s?",
        "-vf", scale_filter,
        "-c:v", "libx264", "-preset", "medium", "-pix_fmt", "yuv420p",
        "-b:v", cfg["maxrate"], "-maxrate", cfg["maxrate"], "-bufsize", cfg["bufsize"],
        "-c:a", "aac", "-b:a", cfg["audio"],
        "-c:s", "mov_text", "-movflags", "+faststart", str(out)
    ]
    p = run(cmd)
    if p.returncode:
        raise RuntimeError(p.stderr[-4000:])
    check = run(["ffmpeg", "-v", "error", "-i", str(out), "-f", "null", "-"])
    if check.returncode or check.stderr.strip():
        raise RuntimeError("corruption gate failed: " + check.stderr[-4000:])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("master", type=Path)
    ap.add_argument("--output-dir", type=Path, default=Path("renditions"))
    ap.add_argument("--profiles", nargs="*", choices=list(PROFILES), default=list(PROFILES))
    ap.add_argument("--manifest", type=Path, default=Path("renditions/manifest.json"))
    a = ap.parse_args()
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            raise SystemExit("missing required tool: " + tool)
    if not a.master.is_file():
        raise SystemExit("master not found: " + str(a.master))
    mm = probe(a.master); md = duration(mm); rows = []
    for name in a.profiles:
        cfg = PROFILES[name]
        out = a.output_dir / (a.master.stem + "." + name.lower() + ".mp4")
        transcode(a.master, out, cfg)
        om = probe(out); validate(mm, om, cfg)
        vb = int(cfg["maxrate"][:-1]) * 1000; ab = int(cfg["audio"][:-1]) * 1000
        rows.append({"profile":name,"file":str(out),"bytes":out.stat().st_size,"sha256":sha256(out),
                     "duration_seconds":duration(om),"video_bitrate_target":cfg["maxrate"],
                     "audio_bitrate_target":cfg["audio"],"estimated_bytes":int(md*(vb+ab)/8),
                     "subtitle_streams":len(streams(om,"subtitle"))})
    a.manifest.parent.mkdir(parents=True, exist_ok=True)
    a.manifest.write_text(json.dumps({"contract":"WETU-CreatorCore-multi-rendition-v1",
        "master":str(a.master),"master_sha256":sha256(a.master),"master_duration_seconds":md,
        "renditions":rows},indent=2),encoding="utf-8")
    print(json.dumps(rows,indent=2))

if __name__ == "__main__":
    try: main()
    except Exception as e:
        print("ERROR:", e, file=sys.stderr); sys.exit(1)
