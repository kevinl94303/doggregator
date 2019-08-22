import dateutil.parser
from bs4 import BeautifulSoup
import re

from crawler import Crawler, OutletCrawler

class WapoCrawler(OutletCrawler):
    def __init__(self):
        self.name = "The Washington Post"
        self.url = "https://www.washingtonpost.com"
        self.re_story = r".com(/[a-z_/-]*/[0-9]{4}/[0-9]{2}/[0-9]{2}/.*)"
        self.re_topic = r".com(/[a-z_/-]*/(?:[a-z_/-]*/)?)"
        self._re_date = re.compile(r"([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}-[0-9])([0-9]{2})")
    
    def get_datetime(self, soup: BeautifulSoup):
        datetimeEl = soup.select_one('span[itemprop*="datePublished"]')
        datetimestr = datetimeEl['content'] if datetimeEl else ""
        match = self._re_date.match(datetimestr)
        if match:
            datetimestr = match.group(1) + ":" + match.group(2)
        datetime = dateutil.parser.parse(datetimestr) if datetimestr else None
        return datetime
    
    def get_lede(self, soup: BeautifulSoup):
        articleBodyEl = soup.select_one('article[itemprop*="articleBody"]')
        if articleBodyEl:
            ledeEl = articleBodyEl.find("p")
            lede = ledeEl.text if ledeEl else ""
        else:
            lede = ""
        
        self.lede = lede
        
        return lede

if __name__ == "__main__":
    wapo_crawler = WapoCrawler()
    crawler = Crawler(wapo_crawler)
    crawler(2)