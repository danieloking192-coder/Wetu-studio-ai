"""Package validated MP4 renditions into HLS and DASH test outputs."""
from __future__ import annotations
import argparse, json, subprocess
from pathlib import Path

PROFILES=(("mobile_saver",854,480,900,64),("mobile",1280,720,1800,96),("standard",1920,1080,3500,128))

def run(cmd): subprocess.run(cmd, check=True)

def package(renditions: Path, output: Path):
    output.mkdir(parents=True, exist_ok=True)
    for name,*_ in PROFILES:
        if not (renditions/f"{name}.mp4").exists(): raise FileNotFoundError(renditions/f"{name}.mp4")
    hls=output/"hls"; hls.mkdir(exist_ok=True)
    variants=[]
    for name,w,h,vb,ab in PROFILES:
        d=hls/name; d.mkdir(exist_ok=True)
        run(["ffmpeg","-y","-i",str(renditions/f"{name}.mp4"),"-c","copy","-f","hls","-hls_time","4","-hls_playlist_type","vod","-hls_segment_filename",str(d/"seg_%03d.ts"),str(d/"index.m3u8")])
        variants.append((name,w,h,vb+ab))
    lines=["#EXTM3U","#EXT-X-VERSION:3"]
    for name,w,h,b in variants:
        lines += [f"#EXT-X-STREAM-INF:BANDWIDTH={b*1000},RESOLUTION={w}x{h}",f"{name}/index.m3u8"]
    (hls/"master.m3u8").write_text("\n".join(lines)+"\n",encoding="utf-8")
    dash=output/"dash"; dash.mkdir(exist_ok=True)
    cmd=["ffmpeg","-y"]+[x for name,*_ in PROFILES for x in ["-i",str(renditions/f"{name}.mp4")]]
    for i in range(3): cmd += ["-map",f"{i}:v","-map",f"{i}:a"]
    cmd += ["-c","copy","-adaptation_sets","id=0,streams=0,2,4 id=1,streams=1,3,5","-seg_duration","4","-use_template","1","-use_timeline","1","-f","dash",str(dash/"manifest.mpd")]
    run(cmd)
    return {"variants":[x[0] for x in variants],"deployment_active":False}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("renditions",type=Path); ap.add_argument("output",type=Path)
    a=ap.parse_args(); r=package(a.renditions,a.output)
    (a.output/"package_manifest.json").write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8")
    print("ADAPTIVE PACKAGE: PASS")
if __name__=="__main__": main()
