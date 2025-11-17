import os
import numpy as np
from PIL import Image
from moviepy import (
    AudioFileClip,
    ImageClip,
    CompositeVideoClip,
)

# =========================
# Configuration / file paths
# =========================
person1_image = r"C:\Users\Hamza\Desktop\podcast\codes\speaker-visualization\video refs\base\a_profile.png"
person2_image = r"C:\Users\Hamza\Desktop\podcast\codes\speaker-visualization\video refs\base\h_profile.png"
audio_file = r"C:\Users\Hamza\Desktop\podcast\edit\ep251\ep251.mp3"

# Replace these with your own timestamp files (start end per line)
person1_timestamps = []
person2_timestamps = []

with open(r"C:\Users\Hamza\Desktop\podcast\edit\ep251\a.txt", 'r') as f:
    for line in f:
        tokens = line.split()
        if len(tokens) >= 2:
            person1_timestamps.append((float(tokens[0]), float(tokens[1])))

with open(r"C:\Users\Hamza\Desktop\podcast\edit\ep251\h.txt", 'r') as f:
    for line in f:
        tokens = line.split()
        if len(tokens) >= 2:
            person2_timestamps.append((float(tokens[0]), float(tokens[1])))


# =========================
# Load audio and get duration
# =========================
audio_clip = AudioFileClip(audio_file)
video_duration = audio_clip.duration


# =========================
# Helpers: precompute color and grayscale numpy arrays from an image
# =========================
def load_image_as_arrays(path):
    pil = Image.open(path).convert("RGB")
    arr = np.array(pil)
    # compute grayscale (uint8)
    gray = (arr[..., 0] * 0.299 + arr[..., 1] * 0.587 + arr[..., 2] * 0.114).astype(np.uint8)
    gray_rgb = np.stack([gray, gray, gray], axis=2)
    return arr, gray_rgb


def build_person_clips(image_path, speaking_times, video_duration, clip_height, position):
    """Return a list of ImageClips (color or grayscale) placed at correct start times.

    This avoids per-frame Python callbacks and is much faster.
    """
    color_arr, gray_arr = load_image_as_arrays(image_path)

    clips = []
    # normalize and resize will be done via ImageClip methods

    # Ensure speaking_times sorted and clipped to duration
    speaking_times = sorted(speaking_times)
    # helper to add a clip
    def add_clip(arr, start, dur):
        if dur <= 0:
            return
        clip = ImageClip(arr).with_start(start).with_duration(dur).resized(height=clip_height).with_position(position)
        clips.append(clip)

    last = 0.0
    for (s, e) in speaking_times:
        # silent gap before this speaking segment
        if s > last:
            add_clip(gray_arr, last, min(s, video_duration) - last)
        # speaking segment (color)
        add_clip(color_arr, max(s, 0.0), max(0.0, min(e, video_duration) - max(s, 0.0)))
        last = max(last, e)

    # trailing silent segment after last speech
    if last < video_duration:
        add_clip(gray_arr, last, video_duration - last)

    return clips


# =========================
# Create person clips using timed ImageClips (fast)
# =========================
print('building clips...')
platform = "youtube"  # options: "tiktok" or "youtube"

if platform == "tiktok":
    video_size = (1080, 1920)  # portrait
    clip_width = int(video_size[0] / 2 * 0.9)
    # we'll pass clip_height later based on image aspect; use a target height
    clip_height = int(video_size[1] * 0.8)
    left_pos = ("left", "center")
    right_pos = ("right", "center")
elif platform == "youtube":
    video_size = (1920, 1080)
    clip_height = int(video_size[1] * 0.8)
    left_pos = ("left", "center")
    right_pos = ("right", "center")
else:
    video_size = (1280, 720)
    clip_height = int(video_size[1] * 0.8)
    left_pos = ("left", "center")
    right_pos = ("right", "center")

clips_person1 = build_person_clips(person1_image, person1_timestamps, video_duration, clip_height, left_pos)
clips_person2 = build_person_clips(person2_image, person2_timestamps, video_duration, clip_height, right_pos)

# =========================
# Combine clips and add audio
# =========================
print('compositing...')
final_clip = CompositeVideoClip(clips_person1 + clips_person2, size=video_size)
final_clip = final_clip.with_audio(audio_clip)


# =========================
# Export settings — tuned for a reasonable speed/quality tradeoff
# - fps: 24 is typical (avoid 1 unless desired)
# - threads: use available CPU cores
# - preset: 'medium' or 'fast' gives good speed without ultra-low quality
# =========================
print('exporting...')
final_clip.write_videofile(
    f"conversation_{platform}.mp4",
    fps=24,
    codec="libx264",
    audio_codec="aac",
    preset="fast",
    threads=8,
)
