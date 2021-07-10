# 导入库
#-*- codeing = utf-8 -*-
#@Time : 2021年5月13日
#@Author : ss
#@File : spider.py
#@Software: vscode

from bs4 import BeautifulSoup     #网页解析，获取数据
import re       #正则表达式，进行文字匹配
import urllib.request,urllib.error      #制定URL，获取网页数据
import csv
import time
#import requests

#影片详情链接的规则
findLink = re.compile(r'<a href="(.*?)">')  
#影片片名
findTitle = re.compile(r'<span class="title">(.*)</span>')
#影片的相关内容
findBd = re.compile(r'<p class="">(.*?)</p>',re.S)

# savepath = "豆瓣电影Top250短评.csv"

def askURL(url):
    '''
    得到指定一个URL的HTML
    '''
    head = {                #模拟浏览器头部信息，向豆瓣服务器发送消息
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    }

    request = urllib.request.Request(url,headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)
    return html


def getMainData(baseurl):
    '''
    爬取一级页面入口：top250的10页，每页25部电影
    '''
    datalist = []
    movie_index = 0

    #for i in range(4,5): 
    for i in range(0,10): #每页(共10页)，每页25部电影
        # datalist = []
        time.sleep(3)
        url = baseurl + str(i*25)
        html = askURL(url)      #保存获取到的网页源码
         
        soup = BeautifulSoup(html,"html.parser")
        for item in soup.find_all('div',class_="item"):     #每部电影
            main_info = []    #保存一部电影的主要信息
            item = str(item)

            titles = re.findall(findTitle,item)     #片名可能只有中文名，没有外国名
            main_info.append(titles[0])

            bd = re.findall(findBd,item)[0]
            bd = re.sub('<br(\s+)?/>(\s+)?'," ",bd)   #去掉<br/>
            bd = bd.strip() #去掉前后的空格
            movie_type = bd.split('/')[-1]
            country = bd.split('/')[-2]
            main_info.append(country) #国家
            main_info.append(movie_type) #类型
            
            movie_index = movie_index + 1
            print("movie "+str(movie_index)+"/250 :" + titles[0]) #第几部电影

            link = re.findall(findLink,item)[0] 
            # print(link)
            comments_info = getCommentData(link) #获取200条短评
            
            for comment_info in comments_info:
                #片名 国家 类型 评分 影评有用投票数 影评
                data = main_info + comment_info
                datalist.append(data) #一条短评完整信息放入datalist

    return datalist #50000条短评信息

def getCommentData(link):
    '''
    link 详情页链接：https://movie.douban.com/subject/1292052/
    短评每页：comments?start=20&limit=20&status=P&sort=new_score，每页20条，仅start=20数字变化
    '''
    comments_info = []

    # for i in range(9,10): #第10页评论
    for i in range(0,10): #10页评论
        time.sleep(2) #评论的每页间隔2s

        url = link + "comments?start=" + str(i*20) + "&limit=20&status=P&sort=new_score"
        html = askURL(url)
        # html = askURL("https://movie.douban.com/subject/1793929/comments?start=180&limit=20&status=P&sort=new_score")

        print("\tcomments page:" + str(i+1) +"/10",end="\t") #爬取i/10页短评
        
        soup = BeautifulSoup(html, 'html.parser')
        for item in soup.find_all('div', attrs={'class': 'comment-item'}):#每页的20条短评
            comment_info = []

            # 评分
            if item.find('span', attrs={'class': 'allstar50 rating'}):
                score = 5
            elif item.find('span', attrs={'class': 'allstar40 rating'}):
                score = 4
            elif item.find('span', attrs={'class': 'allstar30 rating'}):
                score = 3
            elif item.find('span', attrs={'class': 'allstar20 rating'}):
                score = 2
            elif item.find('span', attrs={'class': 'allstar10 rating'}):
                score = 1
            else:
                score = 0
            comment_info.append(score)
            
            # 有用投票
            try:
                vote_count = item.find('span', attrs={'class': 'votes vote-count'}).get_text()
            except:
                vote_count = ""
            # print(vote_count)
            comment_info.append(vote_count)
            
            # 影评
            try:
                comment = item.find('span', attrs={'class': 'short'}).get_text()
            except:
                comment = ""
            comment_info.append(comment)

            comments_info.append(comment_info)
        
        print("end")#一页短评结束

    return comments_info

def saveData(datalist,savepath):
    '''
    保存datalist里的每条数据到指定路径的指定文件savepath
    '''
    print("save to csv...")
    
    #创建csv文件
    f = open(savepath,'w',encoding='utf-8-sig',newline='')
    save_csv = csv.writer(f)

    #片名 国家 类型 评分 影评有用投票数 影评
    col = ["片名","国家","类型","评分","影评投票数","影评"]
    save_csv.writerow(col) #表头

    for i in range(0,50000):
        # print("存入第%d条" %(i+1))
        data = datalist[i]
        # print(data)
        save_csv.writerow(data)
    print("save over!")
    f.close()

def main():
    baseurl = "https://movie.douban.com/top250?start="

    #爬取两级网页
    datalist = getMainData(baseurl)
    savepath = "豆瓣电影Top250短评.csv"
    saveData(datalist,savepath)


if __name__ == "__main__": 
    main()
    print("=======================================")
    print("爬取完毕！")

