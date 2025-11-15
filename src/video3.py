import numpy as np
from moviepy import *

# =========================
# 1. File paths
# =========================
person1_image = r"C:\Users\Hamza\Desktop\podcast\codes\speaker-visualization\video refs\base\a_profile.png"
person2_image = r"C:\Users\Hamza\Desktop\podcast\codes\speaker-visualization\video refs\base\h_profile.png"
audio_file = r"C:\Users\Hamza\Desktop\podcast\edit\ep251\ep251.mp3"

# =========================
# 2. Timestamps (start, end, line_id)
# raw_timestamps = [
#     (0.150, 1.120, 1),
#     (1.770, 2.760, 2),
#     (3.770, 4.350, 3),
#     (12.280, 14.480, 4),
#     (15.310, 15.500, 5),
#     (21.260, 21.530, 6),
#     (29.770, 30.560, 7)
# ]

# # Split timestamps by person (odd lines = person1, even lines = person2)
# person1_timestamps = [(s, e) for s, e, line in raw_timestamps if line % 2 == 1]
# person2_timestamps = [(s, e) for s, e, line in raw_timestamps if line % 2 == 0]

person1_timestamps = []
person2_timestamps = []

with open(r"C:\Users\Hamza\Desktop\podcast\edit\ep251\a.txt", 'r') as f:
    for line in f:
        tokens = line.split()
        person1_timestamps.append((float(tokens[0]), float(tokens[1])))

with open(r"C:\Users\Hamza\Desktop\podcast\edit\ep251\h.txt", 'r') as f:
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
def get_person_clip(image_path, speaking_times, video_duration):
    img = ImageClip(image_path)
    
    def make_frame(t):
        is_speaking = any(start <= t < end for (start, end) in speaking_times)
        frame = img.get_frame(0)
        if not is_speaking:
            gray = frame @ [0.299, 0.587, 0.114]
            frame = np.stack([gray]*3, axis=2)
        return frame
    
    return VideoClip(make_frame, duration=video_duration)

# =========================
# 5. Create clips
clip1 = get_person_clip(person1_image, person1_timestamps, video_duration)
clip2 = get_person_clip(person2_image, person2_timestamps, video_duration)

# =========================
# 6. Choose platform and resize/position
platform = "youtube"  # options: "tiktok" or "youtube"

if platform == "tiktok":
    video_size = (1080, 1920)  # portrait
    clip_width = int(video_size[0] / 2 * 0.9)  # 90% width for padding
    clip1 = clip1.resize(width=clip_width).set_position(("left", "center"))
    clip2 = clip2.resize(width=clip_width).rotate(-5).set_position(("right", "center"))

elif platform == "youtube":
    video_size = (1920, 1080)  # landscape
    clip_height = int(video_size[1] * 0.8)  # 80% height
    clip1 = clip1.resized(height=clip_height).with_position(("left", "center"))
    clip2 = clip2.resized(height=clip_height).with_position(("right", "center"))

# =========================
# 7. Combine clips and add audio
final_clip = CompositeVideoClip([clip1, clip2], size=video_size)
final_clip = final_clip.with_audio(audio_clip)

# Optional: add background color if clips don’t fill frame
# final_clip = final_clip.bg_color(size=video_size, color=(0,0,0))

# =========================
# 8. Export video
final_clip.write_videofile(
    f"conversation_{platform}.mp4",
    fps=24,
    codec="libx264",
    audio_codec="aac",
    preset="medium",
    threads=4
)
