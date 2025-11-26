from pprint import pprint
from mutagen.id3 import ID3, CTOC, CHAP, TIT2, CTOCFlags, ID3NoHeaderError, TPE1, TRCK, APIC
from mutagen.mp3 import MP3 as MUT_MP3


class Tag:
    def __init__(self, metadata, audio):
        self.metadata = metadata
        self.audio = audio
        self.audio_length = int(MUT_MP3(self.audio).info.length) * 1000

        try:
            self.tags = ID3(self.audio, v2_version=3)
        except ID3NoHeaderError:
            self.tags = ID3(v2_version=3)

    def print_tags(self):
        """
        prints tags
        """
        print(self.tags.pprint())

    def add_tags(self):
        """
        adds tags
        """
        # print(self.metadata['Title'][0],type(self.metadata['Title'][0]))
        self.tags.add(TIT2(text=self.metadata["Title"]))
        self.tags.add(TPE1(text=["Time Sink"]))
        self.tags.add(TRCK(text=self.metadata["Track"]))
        self.add_chapters(self.metadata["Chapters"])  # what if no chapters
        self.add_cover_art(self.metadata["Title"])
        
        pprint(self.tags)

        self.tags.save(self.audio, v2_version=3)


    def add_cover_art(self, title):
        """
        adds cover art
        """

        if title.contains("(Movie Plug)"):

            with open(r"images\covart - movie_plug.jpg", "rb") as covart:
                self.tags.add(
                    APIC(
                        encoding=3,        # 3 = UTF-8
                        mime="image/jpeg", # or "image/png"
                        type=3,            # 3 = front cover
                        desc="Cover",
                        data=covart.read()
                    )
            )

    def delete_tags(self):
        """
        deletes tags
        """
        self.tags.delete(self.audio)
        self.tags.save(self.audio, v2_version=3)

    def convert_seconds(self, timestamp):
        """
        converts seconds
        """
        full_time = timestamp.split(":")
        if len(full_time) == 2:
            m, s = full_time
            s_time = int(m) * 60 + int(s)
        else:
            h, m, s = full_time
            s_time = (int(h) * 60 * 60) + (int(m) * 60) + int(s)
        return s_time * 1000

    def add_chapters(self, chapters):
        """
        adds chapters
        """

        self.tags.add(
            CTOC(
                element_id="toc",
                flags=CTOCFlags.TOP_LEVEL | CTOCFlags.ORDERED,
                child_element_ids=[f"chp{i}" for i in range(1, len(chapters) + 1)],
                sub_frames=[
                    TIT2(text=["Table of Contents"]),
                ],
            )
        )

        for i in range(len(chapters)):

            stimestamp, _, chap_title = chapters[i].partition(" ")
            s_time = self.convert_seconds(stimestamp)

            if i + 1 < len(chapters):
                etimestamp, _, _ = chapters[i + 1].partition(" ")
                e_time = self.convert_seconds(etimestamp)
            else:
                e_time = self.audio_length

            self.tags.add(
                CHAP(
                    element_id=f"chp{i+1}",
                    start_time=s_time,
                    end_time=e_time,
                    sub_frames=[
                        TIT2(text=[chap_title]),
                    ],
                )
            )

    # def add_chapters(self, chapters):

    #     self.tags.add(
    #         CTOC(
    #             element_id="toc",
    #             flags=CTOCFlags.TOP_LEVEL | CTOCFlags.ORDERED,
    #             child_element_ids=["chp1","chp2","chp3","chp4","chp5","chp6"],
    #             sub_frames=[
    #                 TIT2(text=["I'm a TOC"]),
    #             ],
    #         )
    #     )

    #     self.tags.add(
    #         CHAP(
    #             element_id="chp1",
    #             start_time=0, end_time=11000,
    #             sub_frames=[
    #                 TIT2(text=["Intro"]),
    #             ],
    #         )
    #     )
    #     self.tags.add(
    #         CHAP(
    #             element_id="chp2",
    #             start_time=11000, end_time=1156000,
    #             sub_frames=[
    #                 TIT2(text=["Do you need to see it all to know your thoughts? Part 2"]),
    #             ],
    #         )
    #     )
    #     self.tags.add(
    #         CHAP(
    #             element_id="chp3",
    #             start_time=1156000, end_time=1658000,
    #             sub_frames=[
    #                 TIT2(text=["Opossum Saved"]),
    #             ],
    #         )
    #     )
    #     self.tags.add(
    #         CHAP(
    #             element_id="chp4",
    #             start_time=1658000, end_time=2325000,
    #             sub_frames=[
    #                 TIT2(text=["Corridor Gets Hacked"]),
    #             ],
    #         )
    #     )
    #     self.tags.add(
    #         CHAP(
    #             element_id="chp5",
    #             start_time=2325000, end_time=3339000,
    #             sub_frames=[
    #                 TIT2(text=["Mark Rober's Scam Call Investigation"]),
    #             ],
    #         )
    #     )
    #     self.tags.add(
    #         CHAP(
    #             element_id="chp6",
    #             start_time=3339000, end_time=3363000,
    #             sub_frames=[
    #                 TIT2(text=["Outro"]),
    #             ],
    #         )
    #     )


# use eyd3
if __name__ == "__main__":
    from drive import Drive
    from docs import Docs

    drive = Drive()
    folder = drive.get_ep_folder_id('S1E1')
    print(f'{folder=}')
    details = drive.get_ep_details_id(folder)
    print(f'{details=}')
    mp3 = drive.download_mp3(folder)
    print(f'{mp3=}')

    docs = Docs()
    doc_content = docs.read_details(details['id'])
    doc_content["Track"] = [folder['name']]
    pprint(doc_content)

    mp3 = Tag(doc_content, mp3['name'])
    mp3.delete_tags()
    mp3.add_tags()
    mp3.print_tags()
