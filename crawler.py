import requests
from bs4 import BeautifulSoup
import re
from typing import Pattern
from datetime import datetime
import dateutil.parser
import os

from keywords import KeywordExtractor
from article import Article
from mysql_api import DB_Connector

class Crawler:

    def __init__(self, outlet: str, url: str, re_story: Pattern, re_topic: Pattern):
        self.outlet = outlet
        self.root_url = url
        self.re_story = re_story
        self.re_topic = re_topic
        self.seen_urls = set([])
        self.dates = []
        self.stories = [] # (url, date, title, keywords[])
        self.keyword_extractor = KeywordExtractor()
        self.conn = DB_Connector("root", os.environ['DOGGREGATOR_PW'], "doggregator.c0k9vwwy6vyu.us-west-1.rds.amazonaws.com", "doggregator")
    
    def __call__(self, depth: int = 2):
        self.crawl(self.root_url, depth)
    
    def update_db(self):
        for date in self.dates:
            print(date)
            self.conn.create_day_table(date)
        for story in self.stories:
            self.conn.insert_article(story)

    def scrape_story(self, url: str):
        print(url)
        if url in self.seen_urls:
            return
        self.seen_urls.add(url)

        try:
            res = requests.get(url)
            res.raise_for_status()
        except:
            print("Failed to GET URL: {}".format(url))
            return
        
        soup = BeautifulSoup(res.text, 'html.parser')

        titleEl = soup.select_one('meta[property="og:title"]')
        title = titleEl['content'] if titleEl else ""

        imgEl = soup.select_one('meta[property="og:image"]')
        img= imgEl['content'] if imgEl else ""


        datetimeEl = soup.select_one('meta[itemprop*="datePublished"]')
        datetime = dateutil.parser.parse(datetimeEl['content']) if datetimeEl else ""

        articleBodyEl = soup.select_one('section[itemprop*="articleBody"]')
        if articleBodyEl:
            ledeEl = articleBodyEl.find("p")
            lede = ledeEl.text if ledeEl else ""
        else:
            lede = ""

        keywords, location = self.keyword_extractor(title, lede)
        if not location:
            location = ""
        
        if datetime.date() not in self.dates:
            self.dates.append(datetime.date())
        
        title = title.replace('\'', '\\\'')

        article = Article(datetime, url, self.outlet, title, img, location, keywords)
        self.stories.append(article)

        return article


    def crawl(self, url: str, depth: int):
        print(url)
        if depth == 0:
            return
        try:
            res = requests.get(url)
            res.raise_for_status()
        except:
            print("Failed to GET URL: {}".format(url))
            return
        
        soup = BeautifulSoup(res.text, 'html.parser')

        for link in soup.find_all('a'):
            href = link.get('href')
            if not href:
                continue

            match = self.re_story.search(href)
            if match:
                self.scrape_story(self.root_url + match.group(1))
                continue

            match = self.re_topic.search(href)
            if match:
                self.crawl(self.root_url + match.group(0), depth - 1)
                continue

        self.update_db()



if __name__ == "__main__":
    nyt_re_story = re.compile(r"((?:/interactive)?/[0-9]{4}/[0-9]{2}/[0-9]{2}/[a-z]*/.*)(#.*)?")
    nyt_re_topic = re.compile(r"/section/.*")
    NYTCrawler = Crawler("The New York Times", "http://www.nytimes.com", nyt_re_story, nyt_re_topic)
    NYTCrawler(1)