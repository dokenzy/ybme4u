# -*- coding: utf-8 -*-

# YBM e4u EngPlaza crawler
# https://github.com/dokenzy/ybme4u
__version__ = '0.1'
__author__ = 'dokenzy@gmail.com'

# http://e4u.ybmsisa.com/EngPlaza/engClass_answer.asp?idx=1103
# http://e4u.ybmsisa.com/EngPlaza/engClass.asp?idx=1110&numIdx=1071

# e4u.ybmsisa.com encoding: euc-kr
# scrapy encoding: utf-8

import re
import datetime

from scrapy.contrib.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import FormRequest

from ybme4u.items import QuestionItem

re_whitespaces = re.compile(r'\s+.+\s+$', re.MULTILINE | re.UNICODE)
re_idx = re.compile(r'engClass\.asp\?idx=(\d+)&numIdx=\d+&page=\d+', re.UNICODE)
answer_url = u'http://e4u.ybmsisa.com/EngPlaza/engClass_answer.asp?idx='


class YBME4USpider(CrawlSpider):
    name = 'ybme4u'
    allowed_domains = ['e4u.ybmsisa.com']
    start_urls = ['http://e4u.ybmsisa.com/EngPlaza/engClass.asp']

    # start point
    def parse(self, response):
        sel = Selector(response)
        links = sel.xpath('//iframe/following-sibling::table[3]/tr/td/a/@href').extract()
        idxs = [re_idx.findall(link)[0] for link in links]

        for idx in idxs:
            yield FormRequest(
                answer_url + idx,
                formdata={},
                callback=self.get_answers
            )

    # informations of single idx
    def get_answers(self, response):
        sel = Selector(response)

        self.node_map = sel.xpath('//map[@name="Map"]')[0]

        idx = int(sel.xpath('//input[@name="idx"]/@value')[0].extract())

        # subject
        node_title = self.node_map.xpath('./following-sibling::tr[3]/td[2]/text()')[0]
        free_title = node_title.extract()

        # date
        node_reg_date = self.node_map.xpath('./following-sibling::tr[5]/td[5]/text()')[0]
        reg_date = node_reg_date.extract().split(' | ')[1]
        reg_date = datetime.datetime.strptime(reg_date, "%Y-%m-%d").date()

        answers = self.get_answer()
        questions = self.get_question()
        cases = self.get_cases()
        descriptions = self.get_description()

        question = QuestionItem()
        question['idx'] = idx
        question['free_title'] = free_title
        question['reg_date'] = reg_date
        question['answer1'] = next(answers)
        question['question1'] = next(questions)
        question['cases1'] = next(cases)
        question['description1'] = next(descriptions)
        question['answer2'] = next(answers)
        question['question2'] = next(questions)
        question['cases2'] = next(cases)
        question['description2'] = next(descriptions)
        question['answer3'] = next(answers)
        question['question3'] = next(questions)
        question['cases3'] = next(cases)
        question['description3'] = next(descriptions)

        return question

    def get_clean_question(self, node):
        return re_whitespaces.sub('', node.extract())[2:]

    def get_clean_answer(self, node):
        return re_whitespaces.sub('', node.extract().split(': ')[1])

    def get_answer(self):
        for table_num in range(1, 8, 3):
            # 마지막 table_num의 실제 값은 8이 아니라 7이다.
            # 7로 하면 마지막에 StopIteration 예외발생,
            # 그래서 3번 문제의 답을 가져오지 못함
            node = './parent::node()/following-sibling::table[%s]/tr/td/table/tr/td[2]/table/tr/td/text()' % (table_num, )
            yield self.get_clean_answer(self.node_map.xpath(node)[1])
        yield

    def get_question(self):
        for table_num in range(2, 9, 3):
            # 마지막 table_num의 실제 값은 9이 아니라 8이다.
            node = './parent::node()/following-sibling::table[%s]/tr[2]/td[1]/text()' % (table_num, )
            yield self.get_clean_question(self.node_map.xpath(node)[1])

    def get_cases(self):
        re_cases = re.compile(r'[a-d] : (\w+)', re.UNICODE)
        for table_num in range(2, 9, 3):
            # 마지막 table_num의 실제 값은 9이 아니라 8이다.
            node = './parent::node()/following-sibling::table[%s]/tr[3]/td/text()' % (table_num, )
            node_cases = self.node_map.xpath(node)
            yield [re_cases.findall(case)[0] for case in node_cases.extract()[0:4]]

    def get_description(self):
        for table_num in range(3, 10, 3):
            # 마지막 table_num의 실제 값은 10이 아니라 9이다.
            node = './parent::node()/following-sibling::table[%s]/tr/td/table/tr[3]/td/text()' % (table_num, )
            node_description = self.node_map.xpath(node)[0]
            yield node_description.extract().encode('utf-8')
