import tkinter
from tkinter import filedialog

import re
import pandas as pd
from datetime import datetime
import io
import csv
import time
from decimal import Decimal
import matplotlib.pyplot as plt
import numpy as np
import datetime

import pytz

root = tkinter.Tk()
root.withdraw()
filename = filedialog.askopenfilename()
print("\ndir_path : ", filename)

with open(filename, 'r', encoding='utf-8') as f:
    chat = f.readlines()
del(chat[0])

p = re.compile("(?P<Datetime>\d{4}\. \d{1,2}\. \d{1,2}\. (오전|오후) \d{1,2}:\d{1,2}), (?P<Username>\w+) : (?P<Contents>[^\n]+)")
del_p = re.compile("(?P<day>\d{4}년 \d{1,2}월 \d{1,2}일 (월|화|수|목|금|토|일)요일)")

new_chat=[]
del_chat =[]

for chatting in chat:
  try:
    m = del_p.search(chatting)
    if m.group("day") is True:
      del chatting
  except AttributeError:
    del_chat.append(chatting)

for chatting in del_chat:
  try:
    m = p.search(chatting)
    if m.group(2) =="오전":
      n= re.sub("오전","am",chatting,1)
    elif m.group(2)=="오후":
      n= re.sub("오후","pm",chatting,1)
    new_chat.append(n)
  except AttributeError:
      pass

  s = re.compile(
      "(?P<Datetime>\d{4}\. \d{1,2}\. \d{1,2}\. \w{2} \d{1,2}:\d{1,2}), (?P<Username>\w+) : (?P<Contents>[^\n]+)")
  kko_parse_result = []

  for chat in new_chat:
      kko_pattern_result = s.findall(chat)
      token = list(kko_pattern_result[0])
      kko_parse_result.append(token)

  kko_parse_result = pd.DataFrame(kko_parse_result, columns=["Datetime", "Speaker", "contents"])
  kko_parse_result.to_csv("kko_regex.csv", index=False)
  df = pd.read_csv("kko_regex.csv")

def preprocessing(text):
    # 개행문자 제거
    text = re.sub('\\\\n', ' ', str(text))
    # 특수문자,자음 제거
    text = re.sub('[.,;:\)*?!~`’^\-_+<>@\#$%&=#/(}※ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎㅠㅜ]', '', text)
    # 중복 생성 공백값
    text = re.sub(' +', ' ', text)
    text = re.sub(' ', '', text)
    return text


# 불용어 제거
def remove_stopwords(text):
    # 띄어쓰기 기준으로 단어삭제# 불용어 제거

    tokens = text.split(' ')
    stops = ['ㅎㅎㅎ', 'ㅎㅎ', 'ㅋㅋ', 'ㅋ', 'ㅎㅎ', 'ㅎ', 'ㅋㅋㅋ', 'ㅋㅋ', 'ㅠㅠㅠㅠ', 'ㅠㅠ',
             "그냥", "거기", "지금", "이제", "우리", "일단", "한번", "나도", "하는", "그게", "약간", "그거", "해서", "재미", "뭔가", "이모티콘",
             "존나", "누가", "하기", "하는데", "거의", "할게", "이번", "이건", "사실", "정도", "갑자기", "혹시", "보고", "하노", ]
    meaningful_words = [w for w in tokens if not w in stops]
    return ' '.join(meaningful_words)


df['new'] = df['contents'].apply(preprocessing)
df['refine_contents'] = df['new'].apply(remove_stopwords)

df.head()

df.drop(['contents','new'],axis=1,inplace=True)

df.to_csv('kakao_text.txt')

def set_data(text_data) :
  with open(text_data, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    data = list(reader)
    return data


text_data = set_data('kakao_text.txt')
data_text = []
for i in text_data :
  data_text.append({'Datetime' : i['Datetime'], 'Speaker' : i['Speaker'], 'refine_contents' : i['refine_contents']})
print(data_text)

pingpong_ = []
time_ = []
for i in data_text :
  time_.append(datetime.datetime.strptime(i['Datetime'], '%Y. %m. %d. %p %I:%M'))

ping = 0
pingpong_.append(0)
print(time_)

for i in range(1, len(time_)) :
  if (time_[i] - time_[i-1]).seconds > 600 :
    ping += 1
  pingpong_.append(ping)

print(pingpong_)

for i in range(0, len(data_text)) :
  data_text[i]['pingpong'] = pingpong_[i]

stick = []
for i in range(0, len(data_text)-1) :
  if data_text[i]['Speaker'] == data_text[i+1]['Speaker'] and data_text[i]['pingpong'] == data_text[i+1]['pingpong'] :
    stick.append(i+1)
stick.reverse()

for i in stick :
  data_text[i-1]['refine_contents'] += data_text[i]['refine_contents']
  del data_text[i]

name = []
#for i in data_text :
#  name.append(i['Speaker'])
#name = set(name)
#name = list(name)
for i in data_text :
    if i['Speaker'] not in name :
        name.append(i['Speaker'])
name_score = []
for i in range(0, len(name)) :
  name_score.append([name[i], str(0.0)])

name_score = dict(name_score)
print(name_score)

def name_score_clear (name_score) :
  name = name_score.keys()
  for i in name :
    name_score[i] = 0
  return name_score

for i in range(0, len(data_text)-1) :
  if i == 0 :
    data_text[i]['starter'] = True
    continue
  if data_text[i]['pingpong'] != data_text[i-1]['pingpong'] and data_text[i]['pingpong'] == data_text[i+1]['pingpong'] :
    data_text[i]['starter'] = True
  else :
    data_text[i]['starter'] = False

data_text[-1]['starter'] = False

check = [-1]
for i in data_text :
  check.append(i['pingpong'])
check.append(-1)

for i in range(1, len(check)-1) :
  if check[i] != check[i-1] and check[i] != check[i+1] :
    data_text[i-1]['comunication'] = False
  else :
    data_text[i-1]['comunication'] = True

def double_plus(a,b) :
  return Decimal(str(a))+Decimal(str(b))

def set_score(text, name_score) :
  count = len(text['refine_contents'])
  num = add_score(name_score, text['starter'])

  ty = 'no_ping'
  if text['comunication'] == True :
    ty = 'pingpong'
  if text['refine_contents'].startswith('파일: ') :
    ty = 'file'

  name_score[text['Speaker']] = double_plus(all_score(ty, count), name_score[text['Speaker']])
  name_score[text['Speaker']] = double_plus(num, name_score[text['Speaker']])
  return name_score

def add_score(name_score, starter) :
  num = 0
  if starter == True :
    num = all_score('starter', 0)
  return num

def all_score(ty, length) :
    no_ping_score = 0                             #pingpong 참여하지 않을 시 점수
    length_score = [0.3, 1.0, 1.5, 1.7, 2.0]      #pingpong 참여시 점수
    length_check = [5, 50, 100, 200]              #글자 수에 따라서
    file_score = 1.0                              #file일 경우
    starter_score = 1.0                           #대화 시작을 할 경우 점수

    if ty == 'file' :
      return file_score
    if ty == 'starter' :
      return starter_score
    #file, starter 점수 부여
    if ty == 'no_ping' :
      return no_ping_score
    #pingpong 참여하지 않을 시 점수출력(0)

    k = 4
    if ty == 'pingpong' :
      for i in range(0, len(length_check)) :
        if length < length_check[i] :
          k = i
          break
      return length_score[k]

    return 0

def print_graph(text, score):
    label_name=[]
    divi = 5
    check = [0]

    for i in range(divi) :
        label_name.append('block'+ str(i))
    #label 이름 설정

    for i in range(1, divi):
        check.append(round(len(text) / divi) * i)
    check.append(len(text))
    #5등분

    score = name_score_clear(score)

    # x = np.arange(divi)
    x = [Decimal(str(1.0))]
    for i in range(1, len(score)):
        x.append(double_plus(x[0], 0.5 * i))

    # block에 따라 score 출력
    # x축: 블록
    # y축: 점수
    width = 0.5
    c = ['black', 'dimgrey', 'darkgray', 'silver', 'lightgrey']
    fig, ax = plt.subplots()
    for i in range(0, divi):
        data = []
        for k in range(check[i], check[i + 1]):
            score = set_score(text[k], score)
        data.append(score.values())

        for idx, item in enumerate(data):
            rects1 = ax.bar(x, list(item), width, color=c)

        for k in range(0, len(score)):
            x[k] += 3

    x_l = []
    x_l.append(2)
    for i in range(1, divi):
        x_l.append(x_l[0]+3*i)

    plt.xticks(x_l, labels=label_name)
    plt.savefig('print_graph.png')
def print_graph_divi(text, score):
    label_name=[]
    divi = 5

    check = [0]

    for i in range(divi) :
        label_name.append('block'+ str(i))
    #label 이름 설정

    for i in range(1, divi):
        check.append(round(len(text) / divi) * i)
    check.append(len(text))
    #5등분

    score = name_score_clear(score)

    # x = np.arange(divi)
    x = [Decimal(str(1.0))]
    for i in range(1, len(score)):
        x.append(double_plus(x[0], 0.5 * i))

    # block에 따라 score 출력
    # x축: 블록
    # y축: 점수
    width = 0.5
    c = ['black', 'dimgrey', 'darkgray', 'silver', 'lightgrey']
    fig, ax = plt.subplots()
    for i in range(0, divi):
        data = []
        score = name_score_clear(score)
        for k in range(check[i], check[i + 1]):
            score = set_score(text[k], score)
        data.append(score.values())

        for idx, item in enumerate(data):
            rects1 = ax.bar(x, list(item), width, color=c)

        for k in range(0, len(score)):
            x[k] += 3

    x_l = []
    x_l.append(2)
    for i in range(1, divi):
        x_l.append(x_l[0]+3*i)

    plt.xticks(x_l, labels=label_name)
    plt.savefig('print_graph_divi.png')
def print_graph_pingpong(text, score):
    divi = len(score)

    score = name_score_clear(score)

    # x = np.arange(divi)
    x = [Decimal(str(1.0))]
    for i in range(1, divi):
        x.append(double_plus(x[0], 0.5 * i))

    # block에 따라 score 출력
    # x축: 블록
    # y축: 점수
    width = 0.5
    c = ['black', 'dimgrey', 'darkgray', 'silver', 'lightgrey']
    fig, ax = plt.subplots()
    for i in range(0, text[-1]['pingpong']):
        data = []

        for k in range(0, len(text)):
            if text[k]['pingpong'] == i:
                score = set_score(text[k], score)
        data.append(score.values())

        for idx, item in enumerate(data):
            rects1 = ax.bar(x, list(item), width, color=c)

        for k in range(0, divi):
            x[k] += 3

    x2 = [2]
    for i in range(0, text[-1]['pingpong'] - 1):
        x2.append(x2[i] + len(score) * 0.5 + 0.5)
    plt.xticks(x2)
    plt.savefig('print_graph_pingpong.png')

def print_divi(text, score):
    divi = 4
    check = [0]

    for i in range(1, divi):
        check.append(round(len(text) / divi) * i)
    check.append(len(text))

    score = name_score_clear(score)

    for i in range(0, divi):
        for k in range(check[i], check[i + 1]):
            score = set_score(text[k], score)
        print(score)
def print_pingpong(text, score) :
  score = name_score_clear(score)
  ping = text[-1]['pingpong']
  check = [0]
  num = 0

  for i in range(0, ping) :
    for k in range(0, len(text)) :
      if i == text[k]['pingpong'] :
        num = k
    check.append(num)

  for i in range(0, ping) :
    for k in range(check[i], check[i+1]) :
      score = set_score(text[k], score)
    print('Block : ', i, ' ', score)
    score = name_score_clear(score)
def print_pingpong_accum(text, score) :
  score = name_score_clear(score)
  ping = text[-1]['pingpong']
  check = [0]
  num = 0

  for i in range(0, ping) :
    for k in range(0, len(text)) :
      if i == text[k]['pingpong'] :
        num = k
    check.append(num)

  for i in range(0, ping) :
    for k in range(check[i], check[i+1]) :
      score = set_score(text[k], score)
    print('Block : ', i, ' ', score)

for i in data_text :
  name_score = set_score(i, name_score)

print_graph(data_text, name_score)
print_graph_divi(data_text, name_score)