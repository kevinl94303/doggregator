import datetime

class Article:
    def __init__(self, datetime: datetime.datetime, link: str, outlet: str, title: str, image: str, location: str, keywords: set):
        self.datetime = datetime
        self.link = link[:512]
        self.outlet = outlet[:512]
        self.title = title[:512]
        self.image = image[:512]
        self.location = location[:512]
        self.keywords = keywords
    
    def __lt__(self, other):
        return self.datetime < other.datetime