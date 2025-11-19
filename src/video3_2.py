import numpy as np
from moviepy import *

# =========================
# 1. File paths
# =========================
# person1_image = r"C:\Users\Hamza\Desktop\podcast\codes\speaker-visualization\video refs\base\a_profile.png"
# person2_image = r"C:\Users\Hamza\Desktop\podcast\codes\speaker-visualization\video refs\base\h_profile.png"
audio_file = r"C:\Users\GH3E\Downloads\ep251.mp3"

person1_timestamps = []
person2_timestamps = []

with open(r"C:\Users\GH3E\Downloads\a.txt", 'r') as f:
    for line in f:
        tokens = line.split()
        person1_timestamps.append((float(tokens[0]), float(tokens[1])))

with open(r"C:\Users\GH3E\Downloads\h.txt", 'r') as f:
    for line in f:
        tokens = line.split()
        person2_timestamps.append((float(tokens[0]), float(tokens[1])))


# print("Person 1 timestamps:", person1_timestamps)
# print("Person 2 timestamps:", person2_timestamps)

# =========================
# # 3. Load audio and get duration
audio_clip = AudioFileClip(audio_file)
video_duration = audio_clip.duration

# =========================
# 4. Function to create speaking clip (grayscale when silent)
def get_person_clip(a_speaking, h_speaking, video_duration):
    # Load static image clips once
    a_gs_h_gs = ImageClip(r"C:\Users\GH3E\Documents\p\speaker-visualization\video refs\a_gs_h_gs-1920x1080.png")
    a_h       = ImageClip(r"C:\Users\GH3E\Documents\p\speaker-visualization\video refs\a_h-1920x1080.png")
    a_hgs     = ImageClip(r"C:\Users\GH3E\Documents\p\speaker-visualization\video refs\a_hgs-1920x1080.png")
    ags_h     = ImageClip(r"C:\Users\GH3E\Documents\p\speaker-visualization\video refs\ags_h-1920x1080.png")

    # Build a sorted list of all time boundaries
    boundaries = {0, video_duration}
    for start, end in a_speaking + h_speaking:
        boundaries.add(start)
        boundaries.add(end)

    boundaries = sorted(boundaries)

    clips = []

    # Build clip segments
    for t0, t1 in zip(boundaries, boundaries[1:]):
        if t1 <= t0:
            continue

        a_on = any(s <= t0 < e for (s, e) in a_speaking)
        h_on = any(s <= t0 < e for (s, e) in h_speaking)

        if a_on and h_on:
            img = a_h
        elif a_on:
            img = a_hgs
        elif h_on:
            img = ags_h
        else:
            img = a_gs_h_gs

        clips.append(img.with_duration(t1 - t0))

    # Concatenate segments
    return concatenate_videoclips(clips, method="chain")


# =========================
# 5. Create clips
print('starting clip1')
clip1 = get_person_clip(person1_timestamps, person2_timestamps, video_duration)

# print('starting clip2')
# clip2 = get_person_clip(person2_image, person2_timestamps, video_duration)

# =========================
# 6. Choose platform and resize/position
platform = "youtube"  # options: "tiktok" or "youtube"

# if platform == "tiktok":
#     video_size = (1080, 1920)  # portrait
#     clip_width = int(video_size[0] / 2 * 0.9)  # 90% width for padding
#     clip1 = clip1.resized(width=clip_width).with_position(("left", "center"))
#     # clip2 = clip2.resize(width=clip_width).rotate(-5).set_position(("right", "center"))

# elif platform == "youtube":
#     video_size = (1920, 1080)  # landscape
#     clip_height = int(video_size[1] * 0.8)  # 80% height
#     clip1 = clip1.resized(height=clip_height).with_position(("left", "center"))
    # clip2 = clip2.resized(height=clip_height).with_position(("right", "center"))

# =========================
# 7. Combine clips and add audio
print('starting CompositeVideoClip')
# final_clip = CompositeVideoClip([clip1, clip2], size=video_size)
final_clip = clip1

print('starting final_clip.with_audio')
final_clip = final_clip.with_audio(audio_clip)

# Optional: add background color if clips don’t fill frame
# final_clip = final_clip.bg_color(size=video_size, color=(0,0,0))

# =========================
# 8. Export video
print('exporting...')

final_clip.write_videofile(
    f"conversation_{platform}.mp4",
    codec="libx264",
    preset="ultrafast",
    ffmpeg_params=["-tune", "stillimage"],
    fps=24,
    audio_codec="aac",
    audio_bitrate="192k"
)

