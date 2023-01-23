import requests
import os
import json
import time
import copy
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.request import urlopen
import re
from pymongo import MongoClient


# 변수 선언
site_url = 'https://m.ppomppu.co.kr'  # 사이트 URL
board_list = []
p_board_list = []
keyword ='맥북'


# 사이트에 파라미터로 넘길 조건들, 키워드 추가시 +뒤에 키워드 추가
params = {
    'search_type': 'subject',
    'keyword': keyword
}


# 조건 추가하여 사이트 오픈
result_search = requests.get('https://m.ppomppu.co.kr/new/bbs_list.php?id=ppomppu&category=4', params=params)


client = MongoClient(host='192.168.30.2', port=27017)
db = client['crawl']['ppomppu']


# 링크에서 금액 찾아서 리턴하는 함수
def get_money(link):
    html = urlopen(link)
    soup = BeautifulSoup(html, 'html.parser', from_encoding='cp949')
    
    try:
        contents = soup.select('div.cont')[0]
        #money_pattern = re.compile('(\d{1,3})+(,\d{3})+')
        money_pattern = re.compile('\d{1,3}(,\d{3})+')
        result = contents.find_all(money_pattern)
        result2 = soup.find('div', {'class':{'cont'}}).find_all(money_pattern)
        result3 = soup.find('div', {'class':{'cont'}}).find_all('p', '')
        
        text = contents.get_text()
        hoho = money_pattern.search(text)
        
        return hoho.group()
        
    except Exception as e:
        print(e)
    


# 사이트 리스트 가져오는 함수
def f_get_list():
    if result_search.status_code == 200:
        html = result_search.text
        soup = BeautifulSoup(html, 'html.parser')
        times = soup.select('#wrap > div.ct > div.bbs > ul > li > a > div.thmb_N2 > ul > li.exp > time')
        titles = soup.select('#wrap > div.ct > div.bbs > ul > li > a > div.thmb_N2 > ul > li.title > span.cont')
        links = soup.select('a.list_b_01n')
        
        return times, titles, links
        


    else:
        print(result_search.status_code)
        
def main():
    while True:
        times, titles, links = f_get_list()  # 게시글 크롤링
        money = []
        
        sms_list = list(set(board_list) - set(p_board_list))  # 이전 리스트와 비교하여 다른 값만 문자 보낼 리스트로 저장
        
        
        for i in range(0, len(titles), 1):
            
            link = site_url + links[i]['href']
            money.append(get_money(link))
            board_list.append('작성시간: ' +times[i].text +'\n제목: ' +titles[i].text.strip() +'\n링크: ' +site_url+links[i]['href'] + '\n가격: ' + str(money[i]))
            
            post = {
                '_id': str(site_url+links[i]['href']),
                'time': str(times[i].text),
                'title': str(titles[i].text.strip()),
                'price': str(money[i]),
                'link': str(site_url+links[i]['href'])
            }    
            
            db.insert_one(post)
            print('insert complete')
        
        

        board_list.clear()
        sms_list.clear()
        time.sleep(1800)  # 반복 주기


if __name__ == "__main__":
    main()