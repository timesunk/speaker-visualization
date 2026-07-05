import subprocess
from pathlib import Path
from pprint import pprint

from moviepy import AudioFileClip

a_speaking = []
h_speaking = []

with open(r"/Users/hamza/Desktop/a.txt", 'r') as f:
    for line in f:
        tokens = line.split()
        # print(tokens)
        a_speaking.append((float(tokens[0]), float(tokens[1])))

with open(r"/Users/hamza/Desktop/h.txt", 'r') as f:
    for line in f:
        tokens = line.split()
        h_speaking.append((float(tokens[0]), float(tokens[1])))

image_paths = {
    "both": r"assets/merged/a line/both.png",
    "a_only": r"assets/merged/a line/a.png",
    "h_only": r"assets/merged/a line/h.png",
    "none": r"/Users/hamza/codes/speaker-visualization/assets/merged/a line/none.png"
}

def convert_to_seconds(ts):
    secs = sum(float(x) * 60 ** i for i, x in enumerate(reversed(ts.split(':'))))
    return secs

def make_clips(clips: list[str], a_speaking, h_speaking):

    for clip in clips:
        times, title = clip.split(maxsplit=1)
        clip_start, clip_end = times.split('-')
        print(clip_start, clip_end)
        # print('after -----------')
        clip_start, clip_end = convert_to_seconds(clip_start), convert_to_seconds(clip_end)
        dur = round(clip_end - clip_start, 4)
        print(dur)
        
        a_sp = [(round(b - clip_start, 4), round(e  - clip_start,4)) for b, e in a_speaking]
        a_sp1 = [(b,e) for b, e in a_sp if e > 0]
        if a_sp1[0][0] < 0: a_sp1[0] = (0, a_sp1[0][1])
        
        a_sp2 = [(b,e) for b, e in a_sp1 if b <= dur]
        if a_sp2[0][1] < dur: a_sp2[-1] = (a_sp2[-1][0], dur)
        # print(a_sp2)

        h_sp = [(round(b - clip_start, 4), round(e  - clip_start,4)) for b, e in h_speaking]
        h_sp1 = [(b,e) for b, e in h_sp if e > 0]
        if h_sp1[0][0] < 0: h_sp1[0] = (0, h_sp1[0][1])
        
        h_sp2 = [(b,e) for b, e in h_sp1 if b <= dur]
        if h_sp2[0][1] < dur: h_sp2[-1] = (h_sp2[-1][0], dur)
        # print(a_sp2)

          # # --- Paths ---
        audio_path = r"/Users/hamza/Desktop/S1E29.mp3"
        output_path = rf"/Users/hamza/Desktop/{title}.mp4"

        audio_clip = AudioFileClip(audio_path)
        audio_duration  = audio_clip.duration

        audio = AudioFileClip(audio_path)

        # Keep audio from 10 seconds to 25 seconds
        trimmed = audio.subclipped(clip_start,clip_end)

        trimmed.write_audiofile("output.mp3")

        audio.close()
        trimmed.close()


        ######---------------------------

        all_times = {0,trimmed.duration}
        for start, end in a_sp2 + h_sp2:
            all_times.update([start, end])

        times = sorted(all_times)


        intervals = []

        ai = 0
        hi = 0
        a_len = len(a_sp2)
        h_len = len(h_sp2)


        for t0, t1 in zip(times, times[1:]):

            while ai < a_len and a_sp2[ai][1] == t0:
                ai += 1

            while hi < h_len and h_sp2[hi][1] == t0:
                hi += 1

            a_on = (ai < a_len and a_sp2[ai][0] == t0)
            h_on = (hi < h_len and h_sp2[hi][0] == t0)

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
                f.write(f"duration {round(dur,4)}\n")
            # Repeat last image to cover audio fully, needed?
            last_img_path = Path(intervals[-1][0]).resolve().as_posix()
            f.write(f"file '{last_img_path}'\n")

        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-i", "output.mp3",
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

        # break

       

if __name__ == "__main__":
    from drive import Drive
    from docs import Docs

    episode = "S1E29"

    drive = Drive()
    folder = drive.get_ep_folder_id(episode)
    print(f'{folder=}')
    details = drive.get_ep_details_id(folder)
    print(f'{details=}')

    docs = Docs()
    doc_content = docs.read_details(details['id'])
    doc_content["Track"] = [folder['name']]
    pprint(doc_content['Clips'])
    make_clips(doc_content['Clips'], a_speaking, h_speaking)

    



# with open(r"/Users/hamza/Desktop/a.txt", 'r') as f:
#     for line in f:
#         tokens = line.split()
#         # print(tokens)
#         a_speaking.append((float(tokens[0]), float(tokens[1])))

# with open(r"/Users/hamza/Desktop/h.txt", 'r') as f:
#     for line in f:
#         tokens = line.split()
#         h_speaking.append((float(tokens[0]), float(tokens[1])))

# image_paths = {
#     "both": r"assets/merged/a line/both.png",
#     "a_only": r"assets/merged/a line/a.png",
#     "h_only": r"assets/merged/a line/h.png",
#     "none": r"/Users/hamza/codes/speaker-visualization/assets/merged/a line/none.png"
# }



# all_times = {0,audio_duration}
# for start, end in a_speaking + h_speaking:
#     all_times.update([start, end])

# times = sorted(all_times)


# intervals = []

# ai = 0
# hi = 0
# a_len = len(a_speaking)
# h_len = len(h_speaking)


# for t0, t1 in zip(times, times[1:]):

#     while ai < a_len and a_speaking[ai][1] == t0:
#         ai += 1

#     while hi < h_len and h_speaking[hi][1] == t0:
#         hi += 1

#     a_on = (ai < a_len and a_speaking[ai][0] == t0)
#     h_on = (hi < h_len and h_speaking[hi][0] == t0)

#     if a_on and h_on:
#         img = image_paths["both"]
#     elif a_on:
#         img = image_paths["a_only"]
#     elif h_on:
#         img = image_paths["h_only"]
#     else:
#         img = image_paths["none"]

#     intervals.append((img, t1 - t0))


# concat_file = "concat_list.txt"
# with open(concat_file, "w") as f:
#     for img, dur in intervals:
#         img_path = Path(img).resolve().as_posix()  # forward slashes for Windows
#         f.write(f"file '{img_path}'\n")
#         f.write(f"duration {dur}\n")
#     # Repeat last image to cover audio fully, needed?
#     last_img_path = Path(intervals[-1][0]).resolve().as_posix()
#     f.write(f"file '{last_img_path}'\n")

# ffmpeg_cmd = [
#     "ffmpeg", "-y",
#     "-f", "concat",
#     "-safe", "0",
#     "-i", str(concat_file),
#     "-i", audio_path,
#     "-c:v", "libx264",           # H.264 ensures full compatibility
#     "-preset", "ultrafast",
#     "-tune", "stillimage",
#     "-pix_fmt", "yuv420p",       # ensures MP4 is playable on all devices
#     "-c:a", "aac",
#     "-b:a", "192k",
#     "-to", str(audio_duration),
#     str(output_path)
# ]

# subprocess.run(ffmpeg_cmd, check=True)

# print("✅ Finished! MP4 created:", output_path)