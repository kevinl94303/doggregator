import json
import mysql.connector
import datetime
import os

from article import Article

class DB_Connector:
    def __init__(self, usr, pwd, url, db):
        """
        constructor to connect to a databse
        """

        # connect to the database
        config = {
                "user": usr,
                "password": pwd,
                "host": url,
                "database": db,
                "raise_on_warnings": True
                }
        
        self.cnx = mysql.connector.connect(**config)
        
        # intialize cursor
        self.mycursor = self.cnx.cursor()
    
    def create_day_table(self, date: datetime.date):
        table_string = "stories-{}-{}-{}".format(date.year, date.month, date.day)
        sql = "SELECT count(*) \
            FROM information_schema.TABLES \
            WHERE (TABLE_SCHEMA = 'doggregator') AND (TABLE_NAME = '{}')".format(table_string)
        
        self.mycursor.execute(sql)
        myresult = self.mycursor.fetchall()

        if(myresult[0][0] == 0):
            sql = "CREATE TABLE `doggregator`.`{}` ( \
                `link` VARCHAR(250) NOT NULL, \
                `location` VARCHAR(45) NOT NULL, \
                `time` DATETIME NOT NULL, \
                `outlet` VARCHAR(45) NOT NULL, \
                `title` VARCHAR(100) NOT NULL, \
                `keywords` TEXT(1000) NOT NULL, \
                `image` VARCHAR(250) NOT NULL, \
                PRIMARY KEY (`link`), \
                INDEX `LOCATION` (`location` ASC) VISIBLE);".format(table_string)

            self.mycursor.execute(sql)
            self.cnx.commit()

    
    def insert_article(self, article: Article):
        date = article.datetime.date()
        table_string = "stories-{}-{}-{}".format(date.year, date.month, date.day)
        sql = "INSERT INTO `doggregator`.`{table}` \
        (`link`, `location`, `time`, `outlet`, `title`, `keywords`, `image`) \
        VALUES ('{link}', '{location}', '{time}', '{outlet}', '{title}', '{keywords}', '{image}') \
        ON DUPLICATE KEY UPDATE link=link;".format(
            table = table_string,
            link = article.link,
            location = article.location,
            time = article.datetime.strftime('%Y-%m-%d %H:%M:%S'),
            outlet = article.outlet,
            title = article.title,
            keywords = ",".join(article.keywords),
            image = article.image
        )

        self.mycursor.execute(sql)
        self.cnx.commit()
    
    def fetch_same_location(self, article: Article):
        date1 = article.datetime.date()
        date2 = article.datetime.date() - datetime.timedelta(days=1)
        table1_string = "stories-{}-{}-{}".format(date1.year, date1.month, date1.day)
        table2_string = "stories-{}-{}-{}".format(date2.year, date2.month, date2.day)

        sql = "SELECT * FROM `doggregator`.`{table1}` t1 \
        WHERE t1.location = '{location}' OR t1.location = '' \
        UNION SELECT * FROM `doggregator`.`{table2}` t2 \
        WHERE t2.location = '{location}' OR t2.location = '';".format(
            table1 = table1_string,
            table2 = table2_string,
            location = article.location,
        )

        self.mycursor.execute(sql)
        myresult = self.mycursor.fetchall()

        return myresult


                    
if __name__ == "__main__":
    conn = DB_Connector("root", os.environ['DOGGREGATOR_PW'], "doggregator.c0k9vwwy6vyu.us-west-1.rds.amazonaws.com", "doggregator")