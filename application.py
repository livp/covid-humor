"""Console application."""
import ctypes
import os
import random

from argparse import ArgumentParser
from datetime import datetime
from typing import List

from tqdm import tqdm
from twarc import Twarc

from configuration import Configuration
from tweet_id_reader import TweetIdReader, Echen102TweetIdReader, TSVTweetReader

ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
CHARACTERS_TO_REMOVE = ['\n', '"']


class Application:
    """Main entry point.

    Args:
        parser (ArgumentParser): command line argument parser.
    """

    def __init__(self, parser: ArgumentParser):
        self.parser: ArgumentParser = parser
        self.configuration: Configuration = Configuration.instance()
        self.date: datetime = None
        self.output_filename = None

    def run(self):
        """Application entry point."""
        self.setup_command_line_arguments()

        if self.input_file is not None:
            date_time_str = os.path.split(self.input_file)[1][4:14]
            self.date = datetime.strptime(date_time_str, "%Y-%m-%d")

            reader = TSVTweetReader()
            twitter_ids: List[str] = reader.read_file(file_name=self.input_file)
            # Extract the date from the file name
        elif self.date is not None:
            reader = Echen102TweetIdReader(base_url=self.configuration["base-url"])
            twitter_ids: List[str] = reader.read_date(self.date)
        else:
            raise Exception("Either --input_file or --date must be specified")

        if len(twitter_ids) == 0:
            print("No tweets were found.")
            return

        print("Shuffling tweets.")
        random.shuffle(twitter_ids)

        with open(self.output_filename, "w", encoding='utf-8') as f:
            count: int = 0
            f.write("day,user,likes,retweets,lang,country code,url,text\n")
            for tweet in self.dehydrate(twitter_ids):
                f.write(self.tweet_to_csv(tweet))
                count += 1

        if not count:
            print("No tweets matching the provided hashtags were found.")
            return

        print("{} tweets exported to {}".format(count, self.output_filename))

    def dehydrate(self, tweet_ids: List[str]):
        t = Twarc(self.configuration["twitter"]["consumer_key"],
                  self.configuration["twitter"]["consumer_secret"],
                  self.configuration["twitter"]["access_token"],
                  self.configuration["twitter"]["access_token_secret"],
                  tweet_mode="extended")
        count: int = 0
        print("Reading tweets from Twitter")
        with tqdm(total=self.configuration["sampling"]["size"], unit="tweet") as written_progress_bar:
            with tqdm(total=len(tweet_ids), unit="tweet") as hydrate_progress_bar:
                for tweet in t.hydrate(tweet_ids):
                    hydrate_progress_bar.update(1)
                    if any(keyword
                           in tweet["full_text"].lower()
                           for keyword in self.configuration["sampling"]["keywords"]):
                        append: bool = True

                        if "only_media" in self.configuration["sampling"].keys():
                            if self.configuration["sampling"]["only_media"]:
                                if not self.contains_media(tweet):
                                    append = False

                        if len(self.configuration["sampling"]["languages"]) > 0:
                            if tweet["lang"] not in self.configuration["sampling"]["languages"]:
                                append = False
                        if append:
                            written_progress_bar.update(1)
                            count += 1
                            yield tweet
                        if count == self.configuration["sampling"]["size"]:
                            return

    def tweet_to_csv(self, tweet):
        id: str = tweet["id_str"]
        if "retweeted_status" in tweet.keys() and "full_text" in tweet["retweeted_status"].keys():
            full_text = self.remove_characters(tweet["retweeted_status"]["full_text"])
        else:
            full_text: str = self.remove_characters(tweet["full_text"])

        user_name: str = self.remove_characters(tweet["user"]["screen_name"])
        likes: int = tweet["favorite_count"]
        retweets: int = tweet["retweet_count"]
        country_code: str = ''
        if tweet["place"] is not None:
            country_code = tweet["place"]["country_code"]
        lang: str = ''
        if tweet["lang"] is not None:
            lang = tweet["lang"]
        media_urls = []
        if self.contains_media(tweet):
            for media_entry in tweet["entities"]["media"]:
                media_urls.append(media_entry["media_url_https"])

        line = '{}/{}/{},{},{},{},{},{},https://twitter.com/i/web/status/{},"{}"'.format(
            self.date.year, str(self.date.month).zfill(2), str(self.date.day).zfill(2),
            user_name,
            likes,
            retweets,
            lang,
            country_code,
            id,
            full_text)
        if len(media_urls) > 0:
            line = line + "," + ",".join(media_urls)
        line = line + "\n"
        return line

    @staticmethod
    def remove_characters(string: str) -> str:
        for character in CHARACTERS_TO_REMOVE:
            string = string.replace(character, '')
        return string

    @staticmethod
    def contains_media(tweet) -> bool:
        if "entities" in tweet.keys():
            entities = tweet["entities"]
            if "media" in entities.keys():
                return True
        return False

    @staticmethod
    def is_retweet(tweet) -> bool:
        return "retweeted_status" in tweet

    def setup_command_line_arguments(self):
        # Options
        self.parser.add_argument("--input-file", help="Extraction File", default=None, type=str, required=False)
        self.parser.add_argument("--date", help="Extraction Date", default=None, type=datetime.fromisoformat, required=False)
        self.parser.add_argument("--output", help="Output file name", default=None, type=str, required=True)
        self.parser.add_argument("--config-file", help="Configuration file", default="config.yaml", type=str, required=False)

        # Parsing
        args = self.parser.parse_args()
        self.date = args.date
        self.input_file = args.input_file
        self.output_filename = args.output

        # Load configuration files
        self.configuration.load_configuration_file(args.config_file)


def disable_windows_sleep():
    if os.name == 'nt':
        print("Preventing Windows from going to sleep")
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)


if __name__ == "__main__":
    disable_windows_sleep()
    application = Application(ArgumentParser())
    application.run()
