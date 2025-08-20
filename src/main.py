from pprint import pprint
from drive import Drive
from docs import Docs
from mp3 import MP3


class TimeSink:
    def __init__(self, ep_num="latest", convert_mp3=True):
        """
        sets variables
        """
        self.ep_num = ep_num
        self.convert_mp3 = convert_mp3
        self.drive = Drive()
        self.docs = Docs()

    def read_details(self):
        """
        Find, reads, and returns the contents of the details file
        """
        id, name = self.drive.find_details(str(self.ep_num))
        if not id:
            return
        doc_content = self.docs.read_details(id)
        doc_content["Track"] = [name]
        self.details = doc_content

    def add_metadata(self, metadata):
        """
        Adds metadata to mp3 files
        """
        mp3_name = self.drive.download_mp3()
        self.mp3 = MP3(metadata, mp3_name)
        self.mp3.delete_tags()
        self.mp3.add_tags()
        self.mp3.print_tags()

    def runner(self):
        """
        begins code execution
        """
        self.read_details()
        print("details", self.details)
        if self.convert_mp3:
            self.add_metadata(self.details)


if __name__ == "__main__":
    TimeSink(ep_num="107", convert_mp3=True).runner()
    # the shownotes may not be fully correct (if more than one link, it will only show the first one)
