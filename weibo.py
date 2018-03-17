import requests
import time
import re
from bs4 import BeautifulSoup
import random
from dbmysql import WeiboDom, engine, WeiboFollow, WeiboUser
from sqlalchemy.orm import sessionmaker
from pymysql.err import InternalError


class WeiBo(object):
    def __init__(self, username, password):
        self.s = requests.session()
        self.login_headers = {'Host': 'passport.weibo.cn',
                    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0',
                    'Accept': '*/*',
                    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate',
                    'Referer': 'https://passport.weibo.cn/signin/login?entry=mweibo&res=wel&wm=3349&r=http%3A%2F%2Fm.weibo.cn%2F',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Connection': 'close'}
        self.headers = {'Host': 'm.weibo.cn',
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Referer': 'https://m.weibo.cn',
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Connection': 'close'}
        self.username = username
        self.login_data = {
        'username': username,
        'password': password,
        'savestate': 1,
        'r': 'http%3A%2F%2Fm.weibo.cn%2F',
        'ec': 0,
        'pagerefer': '',
        'entry': 'mweibo',
        'wentry': '',
        'loginfrom': '',
        'client_id': '',
        'code': '',
        'qq': '',
        'mainpageflag': 1,
        'hff': '',
        'hfp': ''}
        self.cookies = self.verify_cookie()

    def login(self):
        url = 'https://passport.weibo.cn/sso/login'
        r = self.s.post(url, headers=self.login_headers, data=self.login_data)
        if r.json()['retcode'] == 20000000:
            print('登录成功')
            self.save_cookie(r.headers['Set-Cookie'])
            return r.headers['Set-Cookie']
        else:
            print('登录失败，尝试重新登录')
            return None

    def save_cookie(self, cookie):
        with open('%s.txt' % self.username, 'w') as f:
             f.write(cookie)
        print('cookie保存成功')

    def get_cookie(self):
        try:
            with open('%s.txt'%self.username, 'r') as f:
                cookies = {}
                for line in f.read().split(';'):
                    name, value = line.strip().split('=', 1)  # 1代表只分割一次
                    cookies[name] = value
                return cookies
        except:
            return None

    def verify_cookie(self):
        try:
            cookies = self.get_cookie()
            print('cookie获取成功，正在尝试cookie登录')
        except:
            print('cookie过期或不存在')
            cookies = ''
            raise
        url = 'https://m.weibo.cn'
        # params = {'t': str(int(time.time()))}
        r = self.s.get(url, headers=self.headers, cookies=cookies)
        if r.status_code == 200:
            print('登录成功')
            # print(r.text)
            return cookies
        else:
            print('cookie过期,正在尝试重新登录')
            self.login()
            cookies = self.get_cookie()
            # print(cookies)
            return cookies

    def get_user_basic_info(self):
        url = "https://m.weibo.cn/home/me?format=cards"

        r = self.s.get(url, headers=self.headers, cookies=self.cookies)
        try:
            data = r.json()
        except Exception as e:
            print(e)
            data = None
        if not data:
            return None
        user_info = data[0]["card_group"][0]["user"]
        user = {}
        user["user_id"] = user_info["id"]
        user["user_name"] = user_info["name"]
        user["weibo_count"] = user_info["mblogNum"]
        user["follow_count"] = user_info["attNum"]
        return user

    def get_user_follows(self):
        d = self.get_user_basic_info()
        uid = d.get("user_id")
        follow_count = d.get("follow_count")
        if not uid:
            return None
        headers = self.headers
        referer = "https://m.weibo.cn/p/second?containerid=100505" + str(uid) + "_-_FOLLOWERS"
        headers["Referer"] = referer
        page = int(follow_count) // 10 + 1
        follow_list = []
        for i in range(1, int(page) + 1):
            if i == 1:
                url = "https://m.weibo.cn/api/container/getSecond?containerid=100505" + str(uid) + "_-_FOLLOWERS"
            else:
                url = "https://m.weibo.cn/api/container/getSecond?containerid=100505" + str(uid) + "_-_FOLLOWERS&page=" + str(i)
            r = self.s.get(url, headers=headers, cookies=self.cookies)
            try:
                data = r.json()
            except Exception as e:
                print(e)
                data = None
            if not data:
                return None
            follows = data["data"]["cards"] # 这里获取单页所有关注
            if not follows:
                continue
            
            for follow in follows:  # 遍历
                follow_tmp1 = {}  # 临时字典用来存关注的信息
                follow_tmp1["followed_weibo_id"] = follow["user"]["id"]
                follow_tmp1["followed_weibo_name"] = follow["user"]["screen_name"]
                follow_tmp1["weibo_user_id"] = uid
                tmp2 = follow_tmp1.copy()
                follow_list.append(tmp2)
            time.sleep(1)
        return follow_list
                
    def get_st(self):  # st是转发微博post必须的参数
        url = "https://m.weibo.cn/api/config"
        r = self.s.get(url, headers=self.headers, cookies=self.cookies)
        data = r.json()
        st = data["data"]["st"]
        return st
    
    def forward_weibo(self, weibo, content):
        st =  self.get_st()
        url = "https://m.weibo.cn/api/statuses/repost"
        data = {"id": weibo["weibo_content_id"], "content": content, "mid": weibo["mid"], "st": st}
        r = self.s.post(url, data=data, headers=self.headers, cookies=self.cookies)
        if r.json().get("ok") == 1:
            print("转发成功")
            return True

    def get_user_weibo(self, uid):  # 获取前十条微博
        url = "https://m.weibo.cn/api/container/getIndex?uid=" + str(uid) + "&luicode=20000174&type=uid&value=" + str(uid) + "&containerid=107603" + str(uid)
        r = self.s.get(url, headers=self.headers, cookies=self.cookies)
        cards = r.json().get("data").get("cards")
        weibos = []
        for card in cards:
            weibo = {}
            try:
                weibo["weibo_content_id"] = card.get("mblog").get("id")
                weibo["weibo_content"] = card.get("mblog").get("text")
                weibo["weibo_user_id"] = card.get("mblog").get("user").get("id")
                weibo["weibo_username"] = card.get("mblog").get("user").get("screen_name")
                weibo["mid"] = card.get("mblog").get("mid")
            except AttributeError:
                continue  # cards列表里面不一定是微博，用try来过滤
            tmp = weibo.copy()
            weibos.append(tmp)
        return weibos




class WeiboHandle(object):
    def __init__(self, username):
        self.Session = sessionmaker(bind=engine)
        self.uid = self.get_user_id(username)
    
    def dom_weibo(self, weibo):
        session = self.Session()
        result = session.query(WeiboDom).filter_by(mid=weibo["mid"]).first()
        if result:
            print("已存在于数据库")
            return None
        try:
            w = WeiboDom(this_weibo_user_id=str(weibo["weibo_user_id"]), weibo_username=weibo["weibo_username"], weibo_content=weibo["weibo_content"], weibo_content_id=weibo["weibo_content_id"], mid=weibo["mid"], is_forward=0, weibo_user_id=self.uid)
            session.add(w)
            session.commit()
            print("储存成功")
            return 1
        except Exception:
            w = WeiboDom(this_weibo_user_id=str(weibo["weibo_user_id"]), weibo_username=weibo["weibo_username"], weibo_content=None, weibo_content_id=weibo["weibo_content_id"], mid=weibo["mid"], is_forward=0, weibo_user_id=self.uid)
            print("微博内容无法插入")
            return 1
        finally:
            session.close()

    def dom_weibo_follow(self, follow):
        session = self.Session()
        result = session.query(WeiboFollow).filter_by(followed_weibo_id=follow["followed_weibo_id"], weibo_user_id=self.uid).first()
        if result:
            print("已存在于数据库")
            return None
        f = WeiboFollow(followed_weibo_id=follow["followed_weibo_id"], followed_weibo_name=follow["followed_weibo_name"], weibo_user_id=self.uid, is_used=0)
        try:
            session.add(f)
            session.commit()
            print("储存成功")
            return 1
        except Exception as e:
            print(e)
            return None
        finally:
            session.close()

    def dom_user_info(self, username, password, user):
        session = self.Session()
        result = session.query(WeiboUser).filter_by(weibo_id=user["user_id"]).first()
        if result:
            print("已存在于数据库")
            return None
        try:
            weibo_user = WeiboUser(weibo_username=username, weibo_password=password, weibo_id=user["user_id"], weibo_nickname=user["user_name"], weibo_count=user["weibo_count"])
            session.add(weibo_user)
            session.commit()
            print("储存成功")
            return 1
        except Exception as e:
            print(e)
            return None
        finally:
            session.close()
    
    def get_followed_from_database(self):
        session = self.Session()
        follows = session.query(WeiboFollow).filter_by(weibo_user_id=self.uid).all()
        uids = []
        for follow in follows:
            uids.append(follow.followed_weibo_id)
        return uids

    def get_weibo_from_database(self):
        session = self.Session()
        ws = session.query(WeiboDom).filter_by(weibo_user_id=self.uid, is_forward=0).all()
        weibos = []
        for w in ws:
            weibo = {}
            weibo["weibo_content_id"] = w.weibo_content_id
            weibo["mid"] = w.mid
            tmp = weibo.copy()
            weibos.append(tmp)
        
        return weibos

    def update_weibo(self, weibo):  # 用于转发微博后的将数据库的未转发改成已转发
        session = self.Session()
        w  = session.query(WeiboDom).filter_by(mid=weibo["mid"], weibo_user_id=self.uid).first()
        w.is_forward = 1
        print("已更新数据库")
        session.commit()
        session.close()
        
    def get_user_id(self, username):  # uid
        session = self.Session()
        weibo_user = session.query(WeiboUser).filter_by(weibo_username=username).first()
        uid = weibo_user.weibo_id
        return uid