import requests
import os
import json
import time
import copy
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.request import urlopen


# 변수 선언
site_url = 'https://www.ppomppu.co.kr'  # 사이트 URL
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
# print(result_search.url)


# 링크에서 금액 찾아서 리턴하는 함수
def get_money(link):
    html = urlopen(link)
    bs = BeautifulSoup(html, 'html.parser')
    
    try:
        contents = bs.find('td', {'class':{'board-contents'}})
        
        print(contents)
    except:
        print('error occured')
    


# 사이트 리스트 가져오는 함수
def f_get_list():
    if result_search.status_code == 200:
        html = result_search.text
        soup = BeautifulSoup(html, 'html.parser')
        times = soup.select('#wrap > div.ct > div.bbs > ul > li > a > div.thmb_N2 > ul > li.exp > time')
        titles = soup.select('#wrap > div.ct > div.bbs > ul > li > a > div.thmb_N2 > ul > li.title > span.cont')
        links = soup.select('a.list_b_01n')
        
        

        for i in range(0, len(titles), 1):
            board_list.append('작성시간: ' +times[i].text +'\n제목: ' +titles[i].text.strip() +'\n링크: ' +site_url+links[i]['href'])
            
            link = site_url + links[0]['href']
            
            get_money(link)
    else:
        print(result_search.status_code)

while True:
    f_get_list()  # 게시글 크롤링
    sms_list = list(set(board_list) - set(p_board_list))  # 이전 리스트와 비교하여 다른 값만 문자 보낼 리스트로 저장
    
    print(sms_list)

    board_list.clear()
    sms_list.clear()
    time.sleep(1800)  # 반복 주기