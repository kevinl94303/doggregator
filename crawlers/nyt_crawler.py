from crawler import Crawler, OutletCrawler

class NYTCrawler(OutletCrawler):
    def __init__(self):
        self.name = "The New York Times"
        self.url = "http://www.nytimes.com"
        self.re_story = r"((?:/interactive)?/[0-9]{4}/[0-9]{2}/[0-9]{2}/[a-z]*/.*\.html)"
        self.re_topic = r"/section/.*"


if __name__ == "__main__":
    nyt_crawler = NYTCrawler()
    crawler = Crawler(nyt_crawler)
    crawler(2)