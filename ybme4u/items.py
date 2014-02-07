# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class QuestionItem(Item):
    idx = Field()
    free_title = Field()
    reg_date = Field()
    answer1 = Field()
    question1 = Field()
    cases1 = Field()
    description1 = Field()
    answer2 = Field()
    question2 = Field()
    cases2 = Field()
    description2 = Field()
    answer3 = Field()
    question3 = Field()
    cases3 = Field()
    description3 = Field()
