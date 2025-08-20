import cv2
from tqdm import tqdm
import moviepy.editor as mpe


def read_labels():
    """
    reads labels
    """
    with open(r"video refs\labels.txt", "r") as fr:
        end = 0

        for line in fr:
            tokens = line.split()
            if tokens[-1] == "[End]":
                end = int(max(float(tokens[1]) * 100, end))

    slist = [[] for _ in range(end + 1)]

    # print(end, len(slist))

    with open(r"video refs\labels.txt", "r") as fr:
        a = True
        for line in fr:
            tokens = line.split()

            if a and tokens[-1] == "[End]":
                a = False

            lower, upper = int(round(float(tokens[0]) * 100)), int(
                round(float(tokens[1]) * 100)
            )
            # lower_R, upper_R = int(float(tokens[0]) * 100), int(float(tokens[1]) * 100)

            # if lower != lower_R: print(lower, lower_R, tokens[0])
            # if upper != upper_R: print(upper, upper_R, tokens[1])

            if lower == upper:
                continue

            for i in range(lower, upper + 1):
                # if i == lower:
                # print(lower, upper)
                if a:
                    slist[i].append("a")
                else:
                    slist[i].append("h")

        # print(slist)
        slist.append(["d"])
        nlist = []
        prev = []
        counter = 0

        for i, s in enumerate(slist):
            if s == prev:
                counter += 1
            else:
                counter /= 100

                if prev == []:
                    nlist.append((r"video refs\a_h_gs.png", counter))
                elif prev == ["a"]:
                    nlist.append((r"video refs\a_hgs.png", counter))
                elif prev == ["h"]:
                    nlist.append((r"video refs\ags_h.png", counter))
                else:
                    nlist.append((r"video refs\a_h.png", counter))

                prev = s
                counter = 1
        # print(slist[:-100])
        # print(nlist[-1])
        return nlist


def create_video(files_and_duration):
    # Each video has a frame per second which is number of frames in every second
    frame_per_second = 24

    # files_and_duration = [
    #     (r"video refs\a_h_gs.png", d),
    #     (r"video refs\a_h.png", d),
    #     (r"video refs\a_hgs.png", d),
    #     (r"video refs\ags_h.png", d),
    #     # (r"images\file3.jpg", frame_per_second*5),
    # ]

    w, h = 2000, 2000

    fourcc = cv2.VideoWriter_fourcc("m", "p", "4", "v")
    writer = cv2.VideoWriter(r"video refs\output.mp4", fourcc, frame_per_second, (w, h))

    for file, duration in tqdm(files_and_duration):
        frame = cv2.imread(file)
        frame = cv2.resize(frame, (w, h), interpolation=cv2.INTER_AREA)

        ## read files before -> order of files matter
        print(
            duration,
            duration * frame_per_second,
            int(round(duration * frame_per_second)),
        )

        # Repating the frame to fill the duration
        for repeat in range(
            int(round(duration * frame_per_second, 2))
        ):  # might be the problem
            writer.write(frame)

    writer.release()


def combine_vid_aud():
    my_clip = mpe.VideoFileClip(r"video refs\output.mp4")
    audio_background = mpe.AudioFileClip(r"video refs\ep113.mp3")
    final_clip = my_clip.set_audio(audio_background)
    final_clip.write_videofile(r"video refs\final_output.mp4")


def main():
    f = read_labels()
    create_video(f)
    combine_vid_aud()


if __name__ == "__main__":
    main()


# https://stackoverflow.com/questions/21596984/how-to-successfully-use-ffmpeg-to-convert-images-into-videos
# ffmpeg -f concat -i inputs.txt -vf fps=10 -pix_fmt yuv420p output.mp4
# check input.txt
# concat demuxer for ffmpeg
