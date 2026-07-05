import subprocess
from pathlib import Path
from pprint import pprint
from drive import Drive
from docs import Docs
from moviepy import AudioFileClip

class Video:
    def __init__(self):
        '''
        a.txt and h.txt, and more should live on the drive? 
        '''
        self.a_speaking = []
        self.h_speaking = []

        with open(r"/Users/hamza/Desktop/a.txt", 'r') as f:
            for line in f:
                tokens = line.split()
                # print(tokens)
                self.a_speaking.append((float(tokens[0]), float(tokens[1])))

        with open(r"/Users/hamza/Desktop/h.txt", 'r') as f:
            for line in f:
                tokens = line.split()
                self.h_speaking.append((float(tokens[0]), float(tokens[1])))

        self.image_paths = {
            "both": r"assets/merged/a line/both.png",
            "a_only": r"assets/merged/a line/a.png",
            "h_only": r"assets/merged/a line/h.png",
            "none": r"/Users/hamza/codes/speaker-visualization/assets/merged/a line/none.png"
        }

        # # --- Paths ---
        # self.audio_path = r"/Users/hamza/Desktop/S1E29.mp3"
        self.audio_path = r"S1E29.mp3"
        self.audio = AudioFileClip(self.audio_path)
        # self.audio_duration  = audio_clip.duration

        # self.audio = AudioFileClip(self.audio_path)


    def convert_to_seconds(self, ts):
        '''
        Converts different formats to only seconds
        'HH:MM:SS', 'HH:MM:SS.MSS', 'MM:SS', etc.
        '''
        secs = sum(float(x) * 60 ** i for i, x in enumerate(reversed(ts.split(':'))))
        return secs



    def make_clips(self, clips: list[str]):

        for clip in clips:
            times, title = clip.split(maxsplit=1)
            clip_start, clip_end = times.split('-')
            print(clip_start, clip_end)
            # print('after -----------')
            clip_start, clip_end = self.convert_to_seconds(clip_start), self.convert_to_seconds(clip_end)
            dur = round(clip_end - clip_start, 4)
            print(dur)
            
            a_sp = [(round(b - clip_start, 4), round(e  - clip_start,4)) for b, e in self.a_speaking]
            a_sp1 = [(b,e) for b, e in a_sp if e > 0]
            if a_sp1[0][0] < 0: a_sp1[0] = (0, a_sp1[0][1])
            
            a_sp2 = [(b,e) for b, e in a_sp1 if b <= dur]
            if a_sp2[0][1] < dur: a_sp2[-1] = (a_sp2[-1][0], dur)
            # print(a_sp2)

            h_sp = [(round(b - clip_start, 4), round(e  - clip_start,4)) for b, e in self.h_speaking]
            h_sp1 = [(b,e) for b, e in h_sp if e > 0]
            if h_sp1[0][0] < 0: h_sp1[0] = (0, h_sp1[0][1])
            
            h_sp2 = [(b,e) for b, e in h_sp1 if b <= dur]
            if h_sp2[0][1] < dur: h_sp2[-1] = (h_sp2[-1][0], dur)
            # print(a_sp2)


            # Keep audio from 10 seconds to 25 seconds
            output_path = rf"/Users/hamza/Desktop/{title}.mp4"
            

            trimmed = self.audio.subclipped(clip_start, clip_end)
            trimmed.write_audiofile("output.mp3")


            self.make_video(output_path, trimmed, a_sp2, h_sp2)
        
            break
        trimmed.close()  # why does this need to be out here?
        self.audio.close()

    def make_video(self, output_path=r'vid.mp4', audio=[], a_sp2=[], h_sp2=[]):
        '''
        
        '''
        if not a_sp2: 
            a_sp2 = self.a_speaking
            h_sp2 = self.h_speaking
            audio = self.audio

        all_times = {0,audio.duration}
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
                img = self.image_paths["both"]
            elif a_on:
                img = self.image_paths["a_only"]
            elif h_on:
                img = self.image_paths["h_only"]
            else:
                img = self.image_paths["none"]

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
            "-i", "output.mp3",  # needs to be changed to actual audio
            "-c:v", "libx264",           # H.264 ensures full compatibility
            "-preset", "ultrafast",
            "-tune", "stillimage",
            "-pix_fmt", "yuv420p",       # ensures MP4 is playable on all devices
            "-c:a", "aac",
            "-b:a", "192k",
            "-to", str(audio.duration),
            str(output_path)
        ]

        subprocess.run(ffmpeg_cmd, check=True)

        print("✅ Finished! MP4 created:", output_path)


if __name__ == "__main__":

    episode = "S1E29"

    drive = Drive()
    folder = drive.get_ep_folder_id(episode)
    print(f'{folder=}')
    details = drive.get_ep_details_id(folder)
    print(f'{details=}')
    mp3 = drive.download_mp3(folder)
    print(f'{mp3=}')

    docs = Docs()
    doc_content = docs.read_details(details['id'])
    doc_content["Track"] = [folder['name']]
    pprint(doc_content['Clips'])

    vid = Video()
    vid.make_clips(doc_content['Clips'])
    vid.make_video()