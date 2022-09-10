# Twitter Scrapper

A very simple and inefficient Twitter scrapper that drives a Chrome browser to scrape tweets.

USE FOR TESTING PURPOSES ONLY.

## Requirements

- Chrome
- Python 3.9+

## Usage

    python main.py

## Issues

- Tweets are parsed multiple times which is why this program is a little inefficient (might be fixable but would require more testing)
- Can only scrape text based tweets (can be improved but would require some effort)
- Tweets that only contain other tweets like [this one](https://twitter.com/Twitter/status/1494436688554344449?s=20&t=X5aflXAjSNAHkc-HDnMNog) are parsed incorrectly (can be fixed but would require some time and effort)