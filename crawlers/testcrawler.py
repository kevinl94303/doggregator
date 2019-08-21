from crawler import Crawler
import heapq
import re
import os

from mysql_api import DB_Connector

# Write this in rust and port to wasm

nyt_re_story = re.compile(r"((?:/interactive)?/[0-9]{4}/[0-9]{2}/[0-9]{2}/[a-z]*/.*)(#.*)?")
nyt_re_topic = re.compile(r"/section/.*")
NYTCrawler = Crawler("The New York Times", "http://www.nytimes.com", nyt_re_story, nyt_re_topic)

article = NYTCrawler.scrape_story("https://www.nytimes.com/2019/08/20/world/middleeast/syria-idlib-sheikhoun.html")

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