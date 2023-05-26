import pandas as pd
import numpy as np
import argparse
import logging
import re
import jieba
import os
from os import path
from multiprocessing import Pool


# 用于分词的类
# 分词一句评论调用def cut_word(self,sent)
# 分词一个列表调用def cut_sentence(self, sent_list)
class jieba4null():
    """
    docstring for parser_word
    deal处理文本，返回词表、词性及依存关系三个值
    """

    def __init__(self, n_core=16):
        self.rootdir = os.getcwd()
        self.STOP_WORDS_LIST = self.load_txt(path.join(self.rootdir, 'scripts', 'resources', 'stopwords_utf8.txt'))
        self.STOP_WORDS_LIST = set([re.sub('\n', '', item) for item in self.STOP_WORDS_LIST])
        jieba.load_userdict(path.join(self.rootdir, 'scripts', 'resources', 'emotion_user_dict.txt'))
        self.n_CORE = n_core

    def filter_stop(self, input_text):
        for token in input_text:
            if token not in self.STOP_WORDS_LIST:
                yield token

    def cut_word(self, sent):
        words = self.filter_stop(jieba.cut(sent, cut_all=False))
        # words = jieba.cut(sent, cut_all=False)
        result = list(words)
        return list(filter(lambda x: x != '\u200b', result))

    def cut_sentence(self, sent_list):
        result = []
        for sent in sent_list:
            result.append(list(self.cut_word(sent)))
        return result

    def load_txt(self, file):
        with open(file, 'r', encoding='utf-8') as f_h:
            res = [line.encode('utf-8', 'ignore').decode('utf-8', 'ignore') for line in f_h]
            return res


# 用于情绪分析的类(需要分词后)
# 1. 输出结果为数字形式
# 分析一句评论 def single_list_classify(self, seg_list)
# 分析一个列表调用 def multi_list_classify(self, big_seg_list)

# 2. 输出结果为文字形式(积极；消极；中性)
# 分析一句评论 def single_result(self, seg_list)
# 分析一个列表需要先调用def multi_list_classify(self, big_seg_list) 再调用jud(self, seg_list)

class polar_classifier():
    '''
    用于对句子列表进行极性分析的类
    '''

    def __init__(self):
        self.rootdir = os.getcwd()
        self.pos_list = self.load_txt(path.join(self.rootdir, 'scripts', 'resources', 'full_pos_dict_sougou.txt'))
        self.neg_list = self.load_txt(path.join(self.rootdir, 'scripts', 'resources', 'full_neg_dict_sougou.txt'))
        self.degree_dict = pd.read_excel(path.join(self.rootdir, 'scripts', 'resources', 'degree_dict.xlsx'))
        self.deny_dict = ['不', '不是', '没有']

    def load_txt(self, file):
        with open(file, 'r', encoding='gb18030') as f_h:
            res = [line.encode('gb18030', 'ignore').decode('gb18030', 'ignore') for line in f_h]
            result = [re.sub('\n', '', item) for item in res]
            return result

    # 鉴定词汇的情感极性，输入词汇以及正负列表

    def word_polar_classify(self, word, pos_list, neg_list):
        if word in pos_list:
            return 1
        elif word in neg_list:
            return -1
        else:
            return 0

    # 鉴定程度副词，degree:1~6

    def word_strength_classify(self, word, degree_dict):
        sub_dict = degree_dict.loc[degree_dict.word == word, :]
        if sub_dict.shape[0] == 0:
            return 0
        else:
            return sub_dict.iloc[0, 1]

    # 鉴定否定词

    def word_deny_classify(self, word, deny_dict):
        if word in deny_dict:
            return -1
        else:
            return 1

    # 分析单个列表词汇

    def single_list_classify(self, seg_list):
        sign = 1
        k = 1
        result_list = []

        for i, word in enumerate(seg_list):
            polar_temp = self.word_polar_classify(word, self.pos_list, self.neg_list)

            if polar_temp == 0:
                sign *= self.word_deny_classify(word, self.deny_dict)
                k += self.word_strength_classify(word, self.degree_dict)
                result_list.append(polar_temp)
            else:
                result_temp = polar_temp * sign * k
                result_list.append(result_temp)

        if len(result_list) == 0:
            return -100
        else:
            return sum(result_list)

    # 分析多个列表词汇

    def multi_list_classify(self, big_seg_list):

        res = []
        for seg_list in big_seg_list:
            res.append(self.single_list_classify(seg_list))
        senti_list = [x for x in res if x != 'None']
        if len(senti_list) == 0:
            return -100
        else:
            return senti_list

    def single_result(self, seg_list):
        sign = 1
        k = 1
        result_list = []

        for i, word in enumerate(seg_list):
            polar_temp = self.word_polar_classify(word, self.pos_list, self.neg_list)

            if polar_temp == 0:
                sign *= self.word_deny_classify(word, self.deny_dict)
                k += self.word_strength_classify(word, self.degree_dict)
                result_list.append(polar_temp)
            else:
                result_temp = polar_temp * sign * k
                result_list.append(result_temp)

        if len(result_list) == 0:
            return '空数据'
        else:
            if sum(result_list) == 0:
                return '中性'
            elif sum(result_list) > 0:
                return '积极'
            else:
                return '消极'

    def jud(self, seg_list):
        result = []
        for x in seg_list:
            if x > 0:
                result.append('积极')
            elif x < 0:
                result.append('消极')
            else:
                result.append('中性')

        return result


if __name__ == '__main__':
    j = jieba4null()
    res = j.cut_sentence(["情感哈哈哈哈哈意义一亿元，呵呵！", "情感哈哈哈哈哈意义一亿元，呵呵！"])
    print(res)
