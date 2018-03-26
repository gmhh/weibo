import requests
from dbmysql import OneWord, engine, Food
from sqlalchemy.orm import sessionmaker
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
from random import randint, choice
import re
from json import decoder


class origin_weibo():

    def __init__(self, mod):
        self.mod = mod

    def get_content(self):
        content = ''
        return content
    
    def make_content(self): # 这方法用来构造用于转发微博的content
        pass

    def get_pic(self, pic_url, t):  # 指的是原创微博类的类型 
        r = requests.get(pic_url)
        with open("pic/%s.jpg" % t, "wb") as f:
            f.write(r.content)
            print("图片保存成功")
        return True

class one_word(origin_weibo):  # 一言

    def __init__(self):
        self.mod = "一言"
        num = randint(0, 1001)
        self.pic_url = "http://random-pic.oss-cn-hangzhou.aliyuncs.com/pc/" + str(num) + ".jpg"

    def get_content(self):
        types = {
                "a": "动画",
                "b": "漫画",
                "c": "游戏",
                "d": "小说",
                "e": "原创",
                "f": "网络",
                "g": "其他"
            }
        while True:
            url = "https://v1.hitokoto.cn/"
            r = requests.get(url)
            word = r.json()
            if not word:
                continue
            content = word["hitokoto"] + " --- by "  + word["from"]
            return content

    def make_content(self):
        c = self.get_content()
        result = super().get_pic(self.pic_url, "one_word")
        content = "#食品青春# 【{mod}】 {c} @南昌大学食品学院团委@南昌大学食品学院学生会".format(mod=self.mod, c=c)
        return content


class get_weather(origin_weibo):  # 天气

    def __init__(self):
        '''
        参数day 0 表示今天 1 表示明天
        '''
        self.mod = "天气"
        if datetime.now().hour < 12:
            self.day = 0
        elif datetime.now().hour > 12:
            self.day = 1
        num = randint(0, 1001)
        self.pic_url = "http://random-pic.oss-cn-hangzhou.aliyuncs.com/pc/" + str(num) + ".jpg"

    def get_content(self):  # 天气模块
        url = 'http://www.weather.com.cn/weather/101240102.shtml'
        r = requests.get(url)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, 'html.parser')
        weather = soup.find_all('ul', class_='t clearfix')[0].find_all('li')[self.day]
        wea = weather.find('p', class_='wea').text
        tem = weather.find('p', class_='tem').text
        d = date.today() + timedelta(days=self.day)
        content = str(d) + wea + tem
        return content

    def make_content(self):
        c = self.get_content()
        # print(c)
        result = super().get_pic(self.pic_url, "weather")
        content = "#食品青春#{mod}早安！今天 {c} @南昌大学食品学院团委@南昌大学食品学院学生会".format(mod=self.mod, c=c) if self.day == 0 \
                    else "#食品青春#{mod}晚安！明天 {c} @南昌大学食品学院团委@南昌大学食品学院学生会".format(mod=self.mod, c=c)
        return content


class mie_word(origin_weibo):  #咩语

    def __init__(self):
        self.mod = "咩语"
        num = randint(0, 1001)
        self.pic_url = "http://random-pic.oss-cn-hangzhou.aliyuncs.com/pc/" + str(num) + ".jpg"

    def get_content(self):
        url = "http://lab.sangsir.com/api/sentence.php"
        r = requests.get(url)
        content = r.text
        return content

    def make_content(self):
        c = self.get_content()
        result = super().get_pic(self.pic_url, "mie_word")
        content = "#食品青春# 【{mod}】 {c} @南昌大学食品学院团委@南昌大学食品学院学生会".format(mod=self.mod, c=c)
        return content


class recommend_food(origin_weibo):  # 美食推荐

    def __init__(self):
        self.mod = "美食推荐"

    def get_content(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        foods = session.query(Food).filter_by(is_used=0).all()
        food = choice(foods)
        result = super().get_pic(food.food_img, "food")
        content = food.title + " " + food.material + food.food_url
        session.close()
        self.update_food(food.id)
        return content

    def update_food(self, food_id):
        Session = sessionmaker(bind=engine)
        session = Session()
        food = session.query(Food).filter_by(id=food_id)
        food.is_used = 1
        session.commit()
        session.close()

    def make_content(self):
        c = self.get_content()
        content = "#食品青春# 【{mod}】 {c} @南昌大学食品学院团委@南昌大学食品学院学生会".format(mod=self.mod, c=c)
        return content


class daily_news(origin_weibo):  # 每日新闻
    def __init__(self):
        self.mod = "每日国际视野"
    
    def get_content(self):
        url = "http://idaily-cdn.appcloudcdn.com/api/list/v3/android/zh-hans?ver=android&app_ver=36&page=1"
        headers = {"User-Agent": "okhttp/3.3.0"}
        r = requests.get(url, headers=headers)
        try:
            news = r.json()
        except decoder.JSONDecodeError:
            with open("logs/daily_news.log", "a") as f:
                f.write(r.text)
            return None
        new = {}
        new["title_wechat_tml"] = r.json()[0]["title_wechat_tml"]
        new["cover_landscape_hd"] = r.json()[0]["cover_landscape_hd"]
        new["link_share"] = r.json()[0]["link_share"]
        new["content"] = r.json()[0]["content"]
        super().get_pic(new["cover_landscape_hd"], "news")
        content = new["content"] + " --- " + new["title_wechat_tml"] + " " + new["link_share"]
        return content

    def make_content(self):
        c = self.get_content()
        content = "#食品青春# 【{mod}】 {c} @南昌大学食品学院团委@南昌大学食品学院学生会".format(mod=self.mod, c=c)
        return content


class history_of_today():
    def __init__(self):
        self.mod = "历史上的今天"
    
    def get_content(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 7.0; SM-G935P Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.92 Mobile Safari/537.36'}
        url = "https://app.jike.ruguoapp.com/1.0/messages/showDetail?topicId=55557b24e4b058f898707ab5"
        r = requests.get(url, headers=headers)
        try:
            content = r.json()["messages"][0]["content"]
        except decoder.JSONDecodeError:
            with open("logs/daily_news.log", "a") as f:
                f.write(r.text)
            return None
        return content

    def make_content(self):
        c = self.get_content()
        content = "#食品青春# 【{mod}】 {c} @南昌大学食品学院团委@南昌大学食品学院学生会".format(mod=self.mod, c=c)
        return content

h = history_of_today()
print(h.make_content())
        