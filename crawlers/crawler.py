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

class OutletCrawler:
    def __init__(self):
        self.name = ""
        self.url = ""
        self.re_story = ""
        self.re_topic = ""
    
    def init_keyword_extractor(self):
        self.keyword_extractor = KeywordExtractor()

    def get_title(self, soup: BeautifulSoup):
        titleEl = soup.select_one('meta[property="og:title"]')
        title = titleEl['content'] if titleEl else ""
        self.title = title
        return title
    
    def get_img(self, soup: BeautifulSoup):
        imgEl = soup.select_one('meta[property="og:image"]')
        img= imgEl['content'] if imgEl else ""
        return img
    
    def get_datetime(self, soup: BeautifulSoup):
        datetimeEl = soup.select_one('meta[itemprop*="datePublished"]')
        datetime = dateutil.parser.parse(datetimeEl['content']) if datetimeEl else ""
        return datetime
    
    def get_lede(self, soup: BeautifulSoup):
        articleBodyEl = soup.select_one('section[itemprop*="articleBody"]')
        if articleBodyEl:
            ledeEl = articleBodyEl.find("p")
            lede = ledeEl.text if ledeEl else ""
        else:
            lede = ""
        
        self.lede = lede
        
        return lede

    def extract_keywords(self, soup: BeautifulSoup):
        self.init_keyword_extractor()
        keywords, location = self.keyword_extractor(self.title, self.lede)
        if not location:
            location = ""
        
        return keywords, location



class Crawler:

    def __init__(self, outlet_crawler: OutletCrawler):
        self.outlet_crawler = outlet_crawler
        self.outlet = outlet_crawler.name
        self.root_url = outlet_crawler.url
        self.re_story = re.compile(outlet_crawler.re_story)
        self.re_topic = re.compile(outlet_crawler.re_topic)
        self.seen_urls = set([])
        self.dates = []
        self.stories = [] # (url, date, title, keywords[])
        self.conn = DB_Connector("root", os.environ['DOGGREGATOR_PW'], "doggregator.c0k9vwwy6vyu.us-west-1.rds.amazonaws.com", "doggregator")
    
    def __call__(self, depth: int = 2):
        self.crawl(self.root_url, depth)
        self.update_db()
    
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

        title = self.outlet_crawler.get_title(soup)
        img = self.outlet_crawler.get_img(soup)
        datetime = self.outlet_crawler.get_datetime(soup)
        lede = self.outlet_crawler.get_lede(soup)
        keywords, location = self.outlet_crawler.extract_keywords(soup)
        
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