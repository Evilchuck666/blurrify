#!/usr/bin/env python3

import contextlib
import cv2
import glob
import json
import os
import re
import subprocess
from pathlib import Path
from pymediainfo import MediaInfo
from tqdm import tqdm

BLUR_SCRIPT = "haar.py"
CONCAT_CLIPS = "input.txt"
MODEL = "model.xml"
PROCESSED = "processed.json"

AUDIO_EXT = "FLAC"
FRAME_EXT = "BMP"
MP4_EXT = "MP4"
TS_EXT = "TS"

FRAME_PATTERN = f"FRAME_%09d.{FRAME_EXT}"

CONFIG_PATH = os.path.expanduser("~/.config/blurrify/settings.json")
DEFAULTS = {
    "ASSETS_DIR": os.path.expanduser("~/.config/blurrify/assets"),
    "INPUT_DIR": os.path.expanduser("~/Videos"),
    "OUTPUT_DIR": os.path.expanduser("~/Videos/blurred"),
    "TMP_DIR": os.path.expanduser("~/.cache/blurrify/tmp"),
}

def prompt_config():
    config = {}
    for key in list(DEFAULTS.keys()):
        default = DEFAULTS.get(key, "")
        path = input(f"{key} [Default: {default}]: ".strip())
        config[key] = os.path.abspath(os.path.expanduser(path or default))
    return config

def save_config(config):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        f.write(json.dumps(config, indent=4))

def load_config():
    if not os.path.exists(CONFIG_PATH):
        config = prompt_config()
        save_config(config)
    else:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
    return config

def load_processed_videos():
    processed_path = os.path.join(DEFAULTS["ASSETS_DIR"], PROCESSED)
    if os.path.exists(processed_path):
        with open(processed_path, "r") as f:
            return set(json.load(f))
    return set()

def save_processed_videos(basename, processed_videos):
    processed_videos.add(basename)
    processed_path = os.path.join(DEFAULTS["ASSETS_DIR"], PROCESSED)
    with open(processed_path, "w") as f:
        f.write(json.dumps(sorted(processed_videos), indent=4))

conf = load_config()

def prepare_directories():
    os.makedirs(conf["OUTPUT_DIR"], exist_ok=True)
    os.makedirs(conf["TMP_DIR"], exist_ok=True)

def remove_files(directory, pattern="*"):
    for file in glob.glob(os.path.join(directory, pattern)):
        with contextlib.suppress(Exception):
            os.remove(file)

def clean(print_msg=True):
    if print_msg:
        print("\n######## Deleting temporary files (please wait...) ########")
    remove_files(conf["ASSETS_DIR"], f"{CONCAT_CLIPS}")
    remove_files(conf["TMP_DIR"])
    if print_msg:
        print("######## DONE ########")

def get_video_duration(video_path):
    return float(MediaInfo.parse(video_path).tracks[0].duration) / 1000

def parse_time(time_str):
    h, m, s = time_str.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)

def get_frames_number(video_path):
    cap = cv2.VideoCapture(str(video_path))
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return frames

def ffmpeg(cmd, total_duration, pattern, value_parser, desc="Progress: "):
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1) as process:
        pbar = tqdm(total=100, desc=f"{desc:<30}", ncols=75, bar_format="{desc}{bar}| {percentage:3.0f}%")
        last_percent = 0
        for line in process.stdout:
            match = re.search(pattern, line)
            if match:
                current_value = value_parser(match.group(1))
                percent = int((current_value / total_duration) * 100)
                if percent > last_percent:
                    pbar.update(percent - last_percent)
                    last_percent = percent
            elif "progress=end" in line:
                break
        pbar.n = 100
        pbar.refresh()
        pbar.close()

def extract_audio(basename):
    remove_files(conf["TMP_DIR"], f"*.{AUDIO_EXT}")
    video_path = os.path.join(conf["INPUT_DIR"], basename)
    audio_path = os.path.join(conf["TMP_DIR"], f"{os.path.splitext(basename)[0]}.{AUDIO_EXT}")
    duration = get_video_duration(video_path)
    cmd = [
        "ffmpeg", "-hide_banner", "-i", video_path, "-vn", "-acodec", "flac", "-ar", "48000",
        "-sample_fmt", "s32", audio_path, "-y", "-progress", "pipe:1", "-nostats"
    ]
    ffmpeg(
        cmd, total_duration=duration, pattern=r"out_time_ms=(\d+)",
        value_parser=lambda v: int(v), desc=f"Extracting audio"
    )

def create_clips(basename):
    remove_files(conf["TMP_DIR"], f"*.{TS_EXT}")
    output_pattern = f"{conf['TMP_DIR']}/CLIP%01d.{TS_EXT}"
    video_path = os.path.join(conf["INPUT_DIR"], basename)
    duration = get_video_duration(str(video_path))
    segment_duration = duration / 10
    cmd = [
        "ffmpeg", "-i", video_path, "-c", "copy", "-f", "segment", "-segment_time", str(segment_duration),
        "-reset_timestamps", "1", output_pattern, "-y", "-progress", "pipe:1", "-nostats", "-hide_banner"
    ]
    ffmpeg(
        cmd, total_duration=duration, pattern=r"time=(\d+:\d+:\d+\.\d+)",
        value_parser=parse_time, desc=f"Creating clips"
    )

def extract_frames(clip_basename):
    remove_files(conf["TMP_DIR"], f"*.{FRAME_EXT}")
    clip_path = os.path.join(conf["TMP_DIR"], clip_basename)
    duration = get_video_duration(clip_path)
    fps = 60
    cmd = [
        "ffmpeg", "-i", clip_path, "-vf", f"fps={fps}", "-progress", "pipe:1",
        os.path.join(conf["TMP_DIR"], FRAME_PATTERN), "-y", "-nostats", "-hide_banner"
    ]
    ffmpeg(
        cmd, total_duration=duration, pattern=r"time=(\d+:\d+:\d+\.\d+)",
        value_parser=parse_time, desc=f"Extracting {clip_basename} frames"
    )

def apply_blur():
    script_path = os.path.join(conf["ASSETS_DIR"], BLUR_SCRIPT)
    model_path = os.path.join(conf["ASSETS_DIR"], MODEL)
    subprocess.run(["python3", script_path, "--model", model_path, "--directory", conf["TMP_DIR"]])

def join_frames(basename_clip):
    frames_dir = Path(conf["TMP_DIR"])
    total_frames = len(sorted(frames_dir.glob("FRAME_*.BMP")))
    output_path = os.path.join(conf["TMP_DIR"], f"{basename_clip}")
    input_pattern = os.path.join(conf["TMP_DIR"], FRAME_PATTERN)
    cmd = [
        "ffmpeg", "-framerate", "60", "-i", input_pattern, "-c:v", "hevc_nvenc", "-preset", "p1", "-qp", "0",
        "-pix_fmt", "yuv420p", output_path, "-y", "-progress", "pipe:1", "-nostats", "-hide_banner"
    ]
    ffmpeg(
        cmd, total_duration=total_frames, pattern=r"frame=\s*(\d+)",
        value_parser=int, desc="Merging frames: "
    )

def concat_clips():
    scripts_dir = Path(conf["ASSETS_DIR"])
    tmp_dir = Path(conf["TMP_DIR"])
    list_path = scripts_dir / CONCAT_CLIPS
    list_path.unlink(missing_ok=True)
    list_path.touch()
    total_frames = 0

    with list_path.open("w") as f:
        for i in range(10):
            clip_basename = f"CLIP{i}.{TS_EXT}"
            clip_path = tmp_dir / clip_basename
            f.write(f"file '{clip_path}'\n")
            total_frames += get_frames_number(clip_path)

    output_video = f"{conf['TMP_DIR']}/VIDEO.{TS_EXT}"
    cmd = [
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", str(list_path), "-c", "copy",
        f"{output_video}", "-y", "-progress", "pipe:1", "-nostats", "-hide_banner"
    ]
    ffmpeg(
        cmd, total_duration=total_frames, pattern=r"frame=\s*(\d+)",
        value_parser=int, desc=f"Merging clips: "
    )

def mux(basename):
    basename_noext = os.path.splitext(basename)[0]
    input_file = os.path.join(conf["TMP_DIR"], f"VIDEO.{TS_EXT}")
    audio_file = os.path.join(conf["TMP_DIR"], f"{basename_noext}.{AUDIO_EXT}")
    output_file = os.path.join(conf["OUTPUT_DIR"], f"{basename_noext}.{MP4_EXT}")
    total_duration = get_video_duration(input_file)
    cmd = [
        "ffmpeg", "-i", input_file, "-i", audio_file, "-c:v", "hevc_nvenc",
        "-cq", "16", "-preset", "p3", "-c:a", "aac", "-b:a", "320k", "-map",
        "0:v:0", "-map", "1:a:0", "-shortest", output_file, "-y",
        "-progress", "pipe:1", "-nostats", "-hide_banner"
    ]
    ffmpeg(
        cmd, total_duration=total_duration, pattern=r"time=(\d+:\d+:\d+\.\d+)",
        value_parser=parse_time, desc=f"Muxing video and audio"
    )

def process_clips():
    for clip in sorted(glob.glob(os.path.join(conf["TMP_DIR"], f"*.{TS_EXT}"))):
        clip_basename = os.path.basename(clip)
        extract_frames(clip_basename)
        apply_blur()
        join_frames(clip_basename)

def process_videos():
    processed_videos = load_processed_videos()
    for file in sorted(glob.glob(os.path.join(conf["INPUT_DIR"], f"*.{MP4_EXT}"))):
        basename = os.path.basename(file)
        if basename in processed_videos:
            continue
        print(f"\n######## Processing {basename} ########")
        extract_audio(basename)
        create_clips(basename)
        process_clips()
        concat_clips()
        mux(basename)
        save_processed_videos(basename, processed_videos)

def main():
    clean(False)
    prepare_directories()
    process_videos()
    clean()

if __name__ == "__main__":
    main()
