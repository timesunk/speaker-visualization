import subprocess
from pathlib import Path

from moviepy import AudioFileClip

# --- Paths ---
audio_path = r"C:\Users\GH3E\Downloads\ep251.mp3"
output_path = r"C:\Users\GH3E\Downloads\output_fast.mp4"
tmp_dir = Path(r"C:\Users\GH3E\Downloads\tmp_ffmpeg")  # temporary folder for intermediate files
tmp_dir.mkdir(exist_ok=True)

ffmpeg_exe = r"C:\Users\GH3E\Downloads\ffmpeg-local\ffmpeg-local\bin\ffmpeg.exe"

a_speaking = []
h_speaking = []

with open(r"C:\Users\GH3E\Downloads\a.txt", 'r') as f:
    for line in f:
        tokens = line.split()
        a_speaking.append((float(tokens[0]), float(tokens[1])))

with open(r"C:\Users\GH3E\Downloads\h.txt", 'r') as f:
    for line in f:
        tokens = line.split()
        h_speaking.append((float(tokens[0]), float(tokens[1])))

image_paths = {
    "both": r"C:\Users\GH3E\Documents\p\speaker-visualization\video refs\a_h-1920x1080.png",
    "a_only": r"C:\Users\GH3E\Documents\p\speaker-visualization\video refs\a_hgs-1920x1080.png",
    "h_only": r"C:\Users\GH3E\Documents\p\speaker-visualization\video refs\ags_h-1920x1080.png",
    "none": r"C:\Users\GH3E\Documents\p\speaker-visualization\video refs\a_gs_h_gs-1920x1080.png"
}

# --------------------------
# 1. Build a list of unique time boundaries
# --------------------------
all_times = {0}
for start, end in a_speaking + h_speaking:
    all_times.update([start, end])
# add audio duration
audio_clip = AudioFileClip(audio_path)
audio_duration  = audio_clip.duration

times = sorted(all_times)

# --------------------------
# 2. Build intervals with image and duration
# --------------------------
intervals = []
for t0, t1 in zip(times, times[1:]):
    if t1 <= t0:
        continue
    a_on = any(s <= t0 < e for s, e in a_speaking)
    h_on = any(s <= t0 < e for s, e in h_speaking)

    if a_on and h_on:
        img = image_paths["both"]
    elif a_on:
        img = image_paths["a_only"]
    elif h_on:
        img = image_paths["h_only"]
    else:
        img = image_paths["none"]

    intervals.append((img, t1 - t0))

# --------------------------
# 4. Merge consecutive intervals with the same image
# --------------------------
merged_intervals = []
for img, dur in intervals:
    if merged_intervals and merged_intervals[-1][0] == img:
        merged_intervals[-1] = (img, merged_intervals[-1][1] + dur)
    else:
        merged_intervals.append((img, dur))

# --------------------------
# 5. Create FFmpeg concat text file
# --------------------------
concat_file = tmp_dir / "concat_list.txt"
with open(concat_file, "w") as f:
    for img, dur in merged_intervals:
        img_path = Path(img).resolve().as_posix()  # forward slashes for Windows
        f.write(f"file '{img_path}'\n")
        f.write(f"duration {dur}\n")
    # Repeat last image to cover audio fully
    last_img_path = Path(merged_intervals[-1][0]).resolve().as_posix()
    f.write(f"file '{last_img_path}'\n")

# --------------------------
# 6. Run FFmpeg to create fully playable MP4
# --------------------------
ffmpeg_cmd = [
    ffmpeg_exe, "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", str(concat_file),
    "-i", audio_path,
    "-c:v", "libx264",           # H.264 ensures full compatibility
    "-preset", "ultrafast",
    "-tune", "stillimage",
    "-pix_fmt", "yuv420p",       # ensures MP4 is playable on all devices
    "-c:a", "aac",
    "-b:a", "192k",
    "-shortest",
    str(output_path)
]

subprocess.run(ffmpeg_cmd, check=True)

print("✅ Finished! Fully playable ultra-fast MP4 created:", output_path)