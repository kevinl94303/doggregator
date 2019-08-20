from crawler import Crawler
import heapq
import re

# Write this in rust and port to wasm

nyt_re_story = re.compile(r"((?:/interactive)?/[0-9]{4}/[0-9]{2}/[0-9]{2}/[a-z]*/.*)(#.*)?")
nyt_re_topic = re.compile(r"/section/.*")
NYTCrawler = Crawler("The New York Times", "http://www.nytimes.com", nyt_re_story, nyt_re_topic)

article = NYTCrawler.scrape_story("https://www.nytimes.com/2019/08/17/world/asia/hong-kong-protests.html")

NYTCrawler(2)

topstories = []

for story in NYTCrawler.stories:
    sim = len(article.keywords & story.keywords)
    print(story.title, sim)
    if len(topstories) < 5:
        heapq.heappush(topstories, (sim, story))
    else:
        heapq.heappushpop(topstories, (sim, story))

print([(story[0], story[1].link, story[1].title) for story in topstories])