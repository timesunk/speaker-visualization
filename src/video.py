import subprocess
from pathlib import Path

from moviepy import AudioFileClip

# --- Paths ---
audio_path = r"C:\Users\Hamza\Desktop\podcast\edit\S1E2\S1E2.mp3"
output_path = r"C:\Users\Hamza\Desktop\podcast\edit\S1E2\S1E2.mp4"

a_speaking = []
h_speaking = []

with open(r"C:\Users\Hamza\Desktop\podcast\edit\S1E2\a.txt", 'r') as f:
    for line in f:
        tokens = line.split()
        a_speaking.append((float(tokens[0]), float(tokens[1])))

with open(r"C:\Users\Hamza\Desktop\podcast\edit\S1E2\h.txt", 'r') as f:
    for line in f:
        tokens = line.split()
        h_speaking.append((float(tokens[0]), float(tokens[1])))

image_paths = {
    "both": r"C:\Users\Hamza\Desktop\podcast\codes\speaker-visualization\assets\merged\a line\both.png",
    "a_only": r"C:\Users\Hamza\Desktop\podcast\codes\speaker-visualization\assets\merged\a line\a.png",
    "h_only": r"C:\Users\Hamza\Desktop\podcast\codes\speaker-visualization\assets\merged\a line\h.png",
    "none": r"C:\Users\Hamza\Desktop\podcast\codes\speaker-visualization\assets\merged\a line\none.png"
}

audio_clip = AudioFileClip(audio_path)
audio_duration  = audio_clip.duration

all_times = {0,audio_duration}
for start, end in a_speaking + h_speaking:
    all_times.update([start, end])

times = sorted(all_times)


intervals = []

ai = 0
hi = 0
a_len = len(a_speaking)
h_len = len(h_speaking)


for t0, t1 in zip(times, times[1:]):

    while ai < a_len and a_speaking[ai][1] == t0:
        ai += 1

    while hi < h_len and h_speaking[hi][1] == t0:
        hi += 1

    a_on = (ai < a_len and a_speaking[ai][0] == t0)
    h_on = (hi < h_len and h_speaking[hi][0] == t0)

    if a_on and h_on:
        img = image_paths["both"]
    elif a_on:
        img = image_paths["a_only"]
    elif h_on:
        img = image_paths["h_only"]
    else:
        img = image_paths["none"]

    intervals.append((img, t1 - t0))


concat_file = "concat_list.txt"
with open(concat_file, "w") as f:
    for img, dur in intervals:
        img_path = Path(img).resolve().as_posix()  # forward slashes for Windows
        f.write(f"file '{img_path}'\n")
        f.write(f"duration {dur}\n")
    # Repeat last image to cover audio fully, needed?
    last_img_path = Path(intervals[-1][0]).resolve().as_posix()
    f.write(f"file '{last_img_path}'\n")

ffmpeg_cmd = [
    "ffmpeg", "-y",
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
    "-to", str(audio_duration),
    str(output_path)
]

subprocess.run(ffmpeg_cmd, check=True)

print("✅ Finished! MP4 created:", output_path)