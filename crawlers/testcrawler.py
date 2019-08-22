from crawler import Crawler
from nyt_crawler import NYTCrawler
from wapo_crawler import WapoCrawler

import heapq
import re
import os

from mysql_api import DB_Connector

# Write this in rust and port to wasm

# nyt_crawler = NYTCrawler()
# NYTCrawler = Crawler(nyt_crawler)
# article = NYTCrawler.scrape_story("http://www.nytimes.com/2019/08/21/world/europe/greenland-denmark-trump.html")


wapo_crawler = WapoCrawler()
WapoCrawler = Crawler(wapo_crawler)
article = WapoCrawler.scrape_story("https://www.washingtonpost.com/opinions/global-opinions/trumps-denmark-saga-of-the-absurd/2019/08/21/c6cc6880-c44c-11e9-9986-1fb3e4397be4_story.html")

conn = DB_Connector("root", os.environ['DOGGREGATOR_PW'], "doggregator.c0k9vwwy6vyu.us-west-1.rds.amazonaws.com", "doggregator")

stories = conn.fetch_same_location(article)

# NYTCrawler(2)

topstories = []

for story in stories:
    storykeywords = set(story[5].split(','))
    sim = len(article.keywords & storykeywords)
    print(story[4], sim)
    if sim == 0:
        continue
    if len(topstories) < 5:
        heapq.heappush(topstories, (sim, story))
    else:
        heapq.heappushpop(topstories, (sim, story))

print([(story[0], story[1][0], story[1][4]) for story in topstories])