import requests
from dbmysql import OneWord, engine, Food
from sqlalchemy.orm import sessionmaker
from bs4 import BeautifulSoup
from datetime import date
from random import randint, choice
import re
import execjs
from json import decoder


class weibo_extend():

    @staticmethod
    def get_one_word():  # 一言模块
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
            Session = sessionmaker(bind=engine)
            session = Session()
            result = session.query(OneWord).filter_by(id=word["id"]).first()
            if result:
                continue
            content = word["hitokoto"] + " --- by "  + word["from"]
            return content

    @staticmethod
    def dom_one_word(word):  
        if not word:
            print("error")
            return None
        Session = sessionmaker(bind=engine)
        session = Session()
        w = OneWord(id=word["id"], hitokoto=word["hitokoto"], word_type=word["type"], word_from=word["from"], creator=word["creator"], created_at=word["created_at"])
        session.add(w)
        session.commit()
        session.close()
        return True

    @staticmethod
    def get_weather(day):  # 天气模块
        '''
        参数day 0 表示今天 1 表示明天
        '''
        url = 'http://www.weather.com.cn/weather/101240102.shtml'
        r = requests.get(url)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, 'html.parser')
        weather = soup.find_all('ul', class_='t clearfix')[0].find_all('li')[day]
        wea = weather.find('p', class_='wea').text
        tem = weather.find('p', class_='tem').text
        d = date.today()
        w = str(d) + wea + tem
        return w

    @staticmethod
    def get_mie_word():
        num = randint(0, 1001)
        pic_url = "http://random-pic.oss-cn-hangzhou.aliyuncs.com/pc/" + str(num) + ".jpg"
        weibo_extend.get_weibo_pic(pic_url, "mie_word")
        url = "http://lab.sangsir.com/api/sentence.php"
        r = requests.get(url)
        word = r.text
        return word
    
    @staticmethod
    def get_weibo_pic(url, pic_name):
        r = requests.get(url)
        with open("pic/%s.jpg" % pic_name , "wb") as f:
            f.write(r.content)
        return True
    
    @staticmethod
    def recommend_food(url):
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        foods = soup.find_all("li", attrs={"data-id": re.compile(r'^[0-9]')})
        foods_list = []
        food_dic = {}
        for food in foods:
            food_dic["title"] = food.div.a["title"]
            food_dic["food_url"] = food.div.a["href"]
            food_dic["food_img"] = weibo_extend.get_food_img(food_dic["food_url"])
            food_dic["material"] = food.find("p", attrs={"class": "subcontent"}).text
            tmp = food_dic.copy()
            foods_list.append(tmp)
        return foods_list
    
    @staticmethod
    def get_food_img(url):
        r = requests.get(url)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, "html.parser")
        img = soup.find("a", attrs={"class": "J_photo"}).img["src"]
        return img
    
    @staticmethod
    def get_and_save_foods():
        for i in range(1, 21):
            if i == 1:
                url = "http://home.meishichina.com/show-top-type-recipe-order-quarter.html"
            else:
                url = "http://home.meishichina.com/show-top-type-recipe-order-quarter-page-" +str(i) +".html"
            foods = weibo_extend.recommend_food(url)
            for food in foods:
                print(food)
                f = Food(title=food["title"], food_url=food["food_url"], food_img=food["food_img"], material=food["material"], is_used=0)
                try:
                    Session = sessionmaker(bind=engine)
                    session = Session()
                    session.add(f)
                    session.commit()
                    session.close()
                    print("保存成功")
                except Exception as e:
                    print(e)
    @staticmethod
    def get_food_from_database():
        Session = sessionmaker(bind=engine)
        session = Session()
        foods = session.query(Food).filter_by(is_used=0).all()
        food = choice(foods)
        weibo_extend.get_weibo_pic(food.food_img, "food")
        '''r = requests.get(food.food_img)
        with open("pic/food.jpg", "wb") as f:
            f.write(r.content)
            print("图片保存成功")'''
        content = food.title + " " + food.material + food.food_url
        session.close()
        weibo_extend.update_food(food.id)
        return content

    @staticmethod
    def update_food(food_id):
        Session = sessionmaker(bind=engine)
        session = Session()
        food = session.query(Food).filter_by(id=food_id)
        food.is_used = 1
        session.commit()
        session.close()

    @staticmethod
    def get_ncuspy_url():
        url = "http://weixin.sogou.com/weixin?type=1&s_from=input&query=ncuspy%E5%AD%A6%E7%94%9F%E4%BC%9A&ie=utf8&_sug_=n&_sug_type_="
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        spy_url = soup.find("a", attrs={"uigs": "account_name_0"})
        if not spy_url:
            return None
        if spy_url["href"]:
            return spy_url["href"]

    @staticmethod
    def get_lastest(spy_url):
        r = requests.get(spy_url)
        soup = BeautifulSoup(r.text, "html.parser")
        article = soup.find("div", attrs={"class": "weui_msg_card"})
        return article
    
    @staticmethod
    def get_daily_news():
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
        new["cover_thumb"] = r.json()[0]["cover_thumb"]
        new["link_share"] = r.json()[0]["link_share"]
        new["content"] = r.json()[0]["content"]
        weibo_extend.get_weibo_pic(new["cover_thumb"], "daily_new")
        content = new["content"] + " --- " + new["title_wechat_tml"] + new["link_share"]
        return content
        

print(weibo_extend.get_daily_news())