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
    a_gs_h_gs = ImageClip(r"C:\Users\GH3E\Documents\p\speaker-visualization\video refs\a_gs_h_gs.png")
    a_h = ImageClip(r"C:\Users\GH3E\Documents\p\speaker-visualization\video refs\a_h.png")
    a_hgs = ImageClip(r"C:\Users\GH3E\Documents\p\speaker-visualization\video refs\a_hgs.png")
    ags_h = ImageClip(r"C:\Users\GH3E\Documents\p\speaker-visualization\video refs\ags_h.png")
    
    def make_frame(t):
        a_is_speaking = any(start <= t < end for (start, end) in a_speaking)
        h_is_speaking = any(start <= t < end for (start, end) in h_speaking)

        if a_is_speaking and h_is_speaking:
            frame = a_h.get_frame(0)

        elif a_is_speaking and not h_is_speaking:   
            frame = a_hgs.get_frame(0)

        elif not a_is_speaking and h_is_speaking:
            frame = ags_h.get_frame(0)

        else:
            frame = a_gs_h_gs.get_frame(0)

        return frame
    
    return VideoClip(make_frame, duration=video_duration)

# =========================
# 5. Create clips
print('starting clip1')
clip1 = get_person_clip(person1_timestamps, person2_timestamps, video_duration)

# print('starting clip2')
# clip2 = get_person_clip(person2_image, person2_timestamps, video_duration)

# =========================
# 6. Choose platform and resize/position
platform = "youtube"  # options: "tiktok" or "youtube"

if platform == "tiktok":
    video_size = (1080, 1920)  # portrait
    clip_width = int(video_size[0] / 2 * 0.9)  # 90% width for padding
    clip1 = clip1.resize(width=clip_width).set_position(("left", "center"))
    # clip2 = clip2.resize(width=clip_width).rotate(-5).set_position(("right", "center"))

elif platform == "youtube":
    video_size = (1920, 1080)  # landscape
    clip_height = int(video_size[1] * 0.8)  # 80% height
    clip1 = clip1.resized(height=clip_height).with_position(("left", "center"))
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
    fps=24,
    codec="libx264",
    audio_codec="aac",
    preset="fast",
    threads=8,
)
