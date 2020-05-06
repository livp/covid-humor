"""Console application."""
import random

from argparse import ArgumentParser
from datetime import date, datetime
from typing import List

from tqdm import tqdm
from twarc import Twarc

from configuration import Configuration
from tweet_id_reader import TweetIdReader


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
                  self.configuration["twitter"]["access_token_secret"])
        tweets = []
        print("Reading tweets from Twitter")
        with tqdm(total=len(tweet_ids), unit="tweet") as progress_bar:
            for tweet in t.hydrate(tweet_ids):
                progress_bar.update(1)
                if any(keyword in tweet["full_text"].lower() for keyword in self.configuration["sampling"]["keywords"]):
                    tweets.append(tweet)
                    if len(tweets) == self.configuration["sampling"]["size"]:
                        break
        return tweets

    def export_to_csv(self, tweets):
        with open(self.output_filename, "w") as f:
            for tweet in tweets:
                f.write("{}\n".format(tweet["full_text"].replace('\n', '')))

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
    application = Application(ArgumentParser())
    application.run()
