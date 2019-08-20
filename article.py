import datetime

class Article:
    def __init__(self, datetime: datetime.datetime, link: str, outlet: str, title: str, image: str, location: str, keywords: set):
        self.datetime = datetime
        self.link = link
        self.outlet = outlet
        self.title = title
        self.image = image
        self.location = location
        self.keywords = keywords