# 数据清洗
import pandas as pd
import csv

class simhash:
    # 构造函数
    def __init__(self, tokens='', hashbits=128):
        self.hashbits = hashbits
        self.hash = self.simhash(tokens)

    # toString函数
    def __str__(self):
        return str(self.hash)

    # 生成simhash值
    def simhash(self, tokens):
        v = [0] * self.hashbits
        for t in [self._string_hash(x) for x in tokens]:  # t为token的普通hash值
            for i in range(self.hashbits):
                bitmask = 1 << i
                if t & bitmask:
                    v[i] += 1  # 查看当前bit位是否为1,是的话将该位+1
                else:
                    v[i] -= 1  # 否则的话,该位-1
        fingerprint = 0
        for i in range(self.hashbits):
            if v[i] >= 0:
                fingerprint += 1 << i
        return fingerprint  # 整个文档的fingerprint为最终各个位>=0的和

    # 求海明距离
    def hamming_distance(self, other):
        x = (self.hash ^ other.hash) & ((1 << self.hashbits) - 1)
        tot = 0
        while x :
            tot += 1
            x &= x - 1
        return tot

    # 求相似度
    def similarity (self, other):
        a = float(self.hash)
        b = float(other.hash)
        if a > b:
            return b / a
        else:
            return a / b

    # 针对source生成hash值               (一个可变长度版本的Python的内置散列)
    def _string_hash(self, source):
        if source == "":
            return 0
        else:
            x = ord(source[0]) << 7
            m = 1000003
            mask = 2 ** self.hashbits - 1
            for c in source:
                x = ((x * m) ^ ord(c)) & mask
                x ^= len(source)
                if x == -1:
                    x = -2
                return x


if __name__ == '__main__':
    with open('SourceData.csv', 'r', newline='', encoding='utf_8_sig') as f:
        # reader = csv.reader(f)
        reader = csv.reader((line.replace('\0', '') for line in f), delimiter=",")

        # column = [row[5] for row in reader]

        header = next(f)

        rows=[]
        for row in reader:
            rows.append(row[5].split(","))
        for i in range(len(rows)-2):
            s1 =rows[i]
            hash1 = simhash(s1)
            for j in range(i+1,len(rows)-2):
                s2 =rows[j]
                hash2 = simhash(s2)
                print(hash1.hamming_distance(hash2))
                if (hash1.hamming_distance(hash2) <= 3):
                    del rows[j]

df = pd.DataFrame(rows)
df.to_csv("ProcessedData.csv", encoding="utf_8_sig")

f.close()
#
# # 中文分词
#
# import pandas as pd
# import jieba         # 中文分词
# import re            # 用于正则表达式过滤
# # from tqdm import tqdm_notebook   # notebook进度条
# from sklearn.model_selection import train_test_split
# import csv
#
# # 导入数据
# data = pd.read_excel("SourceData.xlsx", names=["电影名","地区","类型","评分","影评投票数","影评"]).astype(str)
# # 获得评论和得分
# comments, score, movie_score = data.values[:,5], data.values[:,4], data.values[:,3]
# data.head()
#
# # 获得电影名与电影类型用于停用词
# movie_name = data.values[:,0]
# movie_type = []
# for i in data.values[:,3]:
#     movie_type += (i.replace('\xa0','').replace('\n'+' '*24,'').split(' '))
# movie_name, movie_type = list(set(movie_name)), list(set(movie_type))
# movie_name, movie_type
#
# def load_stopwords(words, filename):
#     """从词库加载停用词"""
#     with open(f'./stopwords/{filename}','r',encoding='UTF-8') as f:
#         for line in f.readlines():
#             if line.strip('\n') not in words:
#                 words.append(line.strip('\n'))
# stopwords = []
# load_stopwords(stopwords, "stopwords1.txt")
# load_stopwords(stopwords, "stopwords2.txt")
# load_stopwords(stopwords, "stopwords3.txt")
# load_stopwords(stopwords, "stopwords4.txt")
# # 停用词库中加上电影名和电影类型
# stopwords += movie_name + movie_type + ["电影"]
# len(stopwords)
#
# def comment_word_cut(text_list, score, stopwords):
#     """对句子做中文分词"""
#     result, label = [], []
#     # for index in tqdm_notebook(range(len(text_list))):
#     for index in range(len(text_list)):
#         # 去除特殊符号
#         text_list[index] = re.sub("[0-9a-zA-Z\-\s+\.\!\/_,$%^*\(\)\+(+\"\')]+|[+——！，。？、~@#￥%……&*（）<>\[\]:：★◆【】《》;；=?？]+", "",
#                                   text_list[index]).strip()
#         # 中文分词
#         seg_list = jieba.cut(text_list[index], cut_all=False, HMM=True)
#         seg_list = [x.strip('\n')
#                     for x in seg_list if x not in stopwords and len(x) > 1]
#         if len(seg_list) > 1:
#             result.append(seg_list)
#             # 添加得分对应的正、反、中标签
#             if score[index] <= "2":
#                 label.append(-1)
#             elif score[index] >= "4":
#                 label.append(1)
#             else:
#                 label.append(0)
#     return result, label
#
# # 数据集划分与分词
# x_train, x_test, y_train, y_test = train_test_split(comments, movie_score, test_size=0.2, random_state=0)
# train_word_cut, train_label = comment_word_cut(x_train, y_train, stopwords)
# test_word_cut, test_label = comment_word_cut(x_test, y_test, stopwords)
# # 数据集划分与分词
# x_train2, x_test2, y_train2, y_test2 = train_test_split(comments, movie_score, test_size=0.2, random_state=1)
# train_word_cut2, train_label2 = comment_word_cut(x_train2, y_train2, stopwords)
# test_word_cut2, test_label2 = comment_word_cut(x_test2, y_test2, stopwords)
#
# # 生成索引词典
# vocabulary = train_word_cut + test_word_cut
# word2index = {}
# vocabulary_count = 0
# for v in vocabulary:
#     for w in v:
#         if w not in word2index:
#             word2index[w] = vocabulary_count
#             vocabulary_count += 1
# print("vocabulary size: {}".format(vocabulary_count))
#
# # 生成词频词典
# word_freq = {"word":[], "freq":[]}
# for v in vocabulary:
#     for w in v:
#         if w not in word_freq["word"]:
#             word_freq["word"].append(w)
#             word_freq["freq"].append(1)
#         else:
#             word_freq["freq"][word_freq["word"].index(w)] +=1
# # 排序
# # items = list(word_freq.items())
# # items.sort(key=lambda x:x[1],reverse=False)
# # 取前300高频词
# # 保存词频
# df = pd.DataFrame(word_freq)
# df.to_csv("./word_freq.csv", encoding="utf_8_sig")
#
# # 根据索引词典Word2index
# train_index = []
# for w in train_word_cut:
#     train_index.append([word2index[v] for v in w])
# test_index = []
# for w in test_word_cut:
#     test_index.append([word2index[v] for v in w])
# train_index2 = []
# for w in train_word_cut2:
#     train_index2.append([word2index[v] for v in w])
# test_index2 = []
# for w in test_word_cut2:
#     test_index2.append([word2index[v] for v in w])
