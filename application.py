"""Console application."""
import random

from argparse import ArgumentParser
from datetime import date, datetime
from typing import List

from tqdm import tqdm
from twarc import Twarc

from configuration import Configuration
from tweet_id_reader import TweetIdReader


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
        reader = TweetIdReader(self.configuration["base-url"])
        twitter_ids: List[str] = reader.read_date(self.date)
        if len(twitter_ids) == 0:
            print("No tweets were found.")
            return

        random.shuffle(twitter_ids)
        tweets = self.dehydrate(twitter_ids)
        if len(tweets) == 0:
            print("No tweets matching the provided hashtags were found.")
            return

        self.export_to_csv(tweets)
        print("{} tweets exported to {}".format(len(tweets), self.output_filename))

    def dehydrate(self, tweet_ids: List[str]):
        t = Twarc(self.configuration["twitter"]["consumer_key"],
                  self.configuration["twitter"]["consumer_secret"],
                  self.configuration["twitter"]["access_token"],
                  self.configuration["twitter"]["access_token_secret"],
                  tweet_mode="extended")
        tweets = []
        print("Reading tweets from Twitter")
        with tqdm(total=self.configuration["sampling"]["size"], unit="tweet") as written_progress_bar:
            with tqdm(total=len(tweet_ids), unit="tweet") as hydrate_progress_bar:
                for tweet in t.hydrate(tweet_ids):
                    hydrate_progress_bar.update(1)
                    if any(keyword
                           in tweet["full_text"].lower()
                           for keyword in self.configuration["sampling"]["keywords"]):
                        append: bool = True
                        if len(self.configuration["sampling"]["languages"]) > 0:
                            if tweet["lang"] not in self.configuration["sampling"]["languages"]:
                                append = False
                        if append:
                            tweets.append(tweet)
                            written_progress_bar.update(1)
                        if len(tweets) == self.configuration["sampling"]["size"]:
                            break
        return tweets

    def export_to_csv(self, tweets):
        with open(self.output_filename, "w", encoding='utf-8') as f:
            f.write("day,user,likes,retweets,lang,country code,text\n")
            for tweet in tweets:
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

                f.write('{}/{}/{},{},{},{},{},{},"{}"\n'.format(
                    self.date.year, str(self.date.month).zfill(2), str(self.date.day).zfill(2),
                    user_name,
                    likes,
                    retweets,
                    lang,
                    country_code,
                    full_text))

    @staticmethod
    def remove_characters(string: str) -> str:
        for character in CHARACTERS_TO_REMOVE:
            string = string.replace(character, '')
        return string

    def setup_command_line_arguments(self):
        # Options
        self.parser.add_argument("--date", help="Extraction Date", default=None, type=datetime.fromisoformat, required=True)
        self.parser.add_argument("--output", help="Output file name", default=None, type=str, required=True)
        self.parser.add_argument("--config-file", help="Configuration file", default="config.yaml", type=str, required=False)

        # Parsing
        args = self.parser.parse_args()
        self.date = args.date
        self.output_filename = args.output

        # Load configuration files
        self.configuration.load_configuration_file(args.config_file)


if __name__ == "__main__":
    import sys
    print(sys.path)
    application = Application(ArgumentParser())
    application.run()
