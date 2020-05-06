import urllib.request
from datetime import datetime
from typing import List


class TweetIdReader:

    def __init__(self, base_url: str):
        self.base_url = base_url

    def read_date(self, date: datetime):
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
