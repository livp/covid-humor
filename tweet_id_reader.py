import urllib.request
from abc import abstractmethod, ABC
from datetime import datetime
from typing import List


class TweetIdReader(ABC):

    def __init__(self, base_url: str = None):
        self.base_url = base_url

    @abstractmethod
    def read_date(file_name: str = None):
        pass

    @abstractmethod
    def read_file(file_name: str = None):
        pass


class Echen102TweetIdReader(TweetIdReader):

    def read_date(self, date: datetime = None):
        print("Reading tweet list for {}/{}/{}".format(date.year, str(date.month).zfill(2), str(date.day).zfill(2)))

        twitter_ids: List[str] = []
        for i in range(24):
            url: str = "{}/{}-{}/coronavirus-tweet-id-{}-{}-{}-{}.txt".format(
                self.base_url,
                date.year, str(date.month).zfill(2),
                date.year, str(date.month).zfill(2), str(date.day).zfill(2),
                str(i).zfill(2)
            )
            try:
                with urllib.request.urlopen(urllib.request.Request(url)) as response:
                    lines: List[str] = (response.read().decode("utf-8").splitlines())
                    twitter_ids.extend(lines)
                    print("Read {} lines from {}".format(len(lines), url))
            except urllib.error.HTTPError as error:
                if error.code == 404:
                    break
                else:
                    raise Exception("Unable to download tweet list: {}".format(url))
        print("Total: {} tweets".format(len(twitter_ids)))
        return twitter_ids

    def read_file(self, file_name: str = None):
        raise Exception("Not implemented")


class TSVTweetReader(TweetIdReader):

    def read_date(self, date: datetime = None, file_name: str = None):
        raise Exception("Not implemented")

    def read_file(self, file_name: str = None):
        print("Reading tweet from {}".format(file_name))

        twitter_ids: List[str] = []
        file = open(file_name, "r")
        header: bool = True
        for line in file:
            if header:
                header = False
                continue
            twitter_ids.append(line.split('\t')[0])
        print("Total: {} tweets".format(len(twitter_ids)))
        return twitter_ids
