import requests
from dbmysql import OneWord, engine, Food
from sqlalchemy.orm import sessionmaker
from bs4 import BeautifulSoup
from datetime import date
from random import randint, choice
import re




class weibo_extend():
    def get_one_word():
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
            content = weibo_extend.make_weibo_content(word)
            return content

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

    def make_weibo_content(word):
        types = {
                "a": "动画",
                "b": "漫画",
                "c": "游戏",
                "d": "小说",
                "e": "原创",
                "f": "网络",
                "g": "其他"
            }
        
        content = word["hitokoto"] + " --- by "  + word["from"]
        return content

    def get_weather():
        url = 'http://www.weather.com.cn/weather/101240102.shtml'
        r = requests.get(url)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, 'html.parser')
        weather = soup.find_all('ul', class_='t clearfix')[0].find_all('li')[0]
        wea = weather.find('p', class_='wea').text
        tem = weather.find('p', class_='tem').text
        d = date.today()
        w = str(d) + wea + tem
        return w

    def get_mie_word():
        url = "http://lab.sangsir.com/api/sentence.php"
        r = requests.get(url)
        word = r.text
        return word

    def get_weibo_pic():
        num = randint(0, 1001)
        url = "http://random-pic.oss-cn-hangzhou.aliyuncs.com/pc/" + str(num) + ".jpg"
        r = requests.get(url)
        with open("pic/mie_word.jpg", "wb") as f:
            f.write(r.content)
        return True

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

    def get_food_img(url):
        r = requests.get(url)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, "html.parser")
        img = soup.find("a", attrs={"class": "J_photo"}).img["src"]
        return img
        
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

    def get_food_from_database():
        Session = sessionmaker(bind=engine)
        session = Session()
        foods = session.query(Food).filter_by(is_used=0).all()
        food = choice(foods)
        r = requests.get(food.food_img)
        with open("pic/food.jpg", "wb") as f:
            f.write(r.content)
            print("图片保存成功")
        content = food.title + " " + food.material + food.food_url
        session.close()
        weibo_extend.update_food(food.id)
        return content

    def update_food(food_id):
        Session = sessionmaker(bind=engine)
        session = Session()
        food = session.query(Food).filter_by(id=food_id)
        food.is_used = 1
        session.commit()
        session.close()