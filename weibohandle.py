import requests
import time
from dbmysql import WeiboDom, engine, WeiboFollow, WeiboUser
from sqlalchemy.orm import sessionmaker
from random import choice
from weibo import WeiBo


class WeiboHandle(object):
    def __init__(self, username, password):
        self.Session = sessionmaker(bind=engine)
        self.username = username
        self.password = password
        self.uid = self.get_user_id(username)

    def dom_weibo(self, weibo):
        session = self.Session()
        result = session.query(WeiboDom).filter_by(mid=weibo["mid"]).first()
        if result:
            print("已存在于数据库")
            return None
        try:
            w = WeiboDom(this_weibo_user_id=str(weibo["weibo_user_id"]), weibo_username=weibo["weibo_username"],
                         weibo_content=weibo["weibo_content"], weibo_content_id=weibo["weibo_content_id"],
                         mid=weibo["mid"], is_forward=0, weibo_user_id=self.uid)
            session.add(w)
            session.commit()
            print("储存成功")
            return 1
        except Exception:
            w = WeiboDom(this_weibo_user_id=str(weibo["weibo_user_id"]), weibo_username=weibo["weibo_username"],
                         weibo_content=None, weibo_content_id=weibo["weibo_content_id"], mid=weibo["mid"], is_forward=0,
                         weibo_user_id=self.uid)
            print("微博内容无法插入")
            return 1
        finally:
            session.close()

    def dom_weibo_follow(self, follow):
        session = self.Session()
        result = session.query(WeiboFollow).filter_by(followed_weibo_id=follow["followed_weibo_id"],
                                                      weibo_user_id=self.uid).first()
        if result:
            print("已存在于数据库")
            return None
        f = WeiboFollow(followed_weibo_id=follow["followed_weibo_id"],
                        followed_weibo_name=follow["followed_weibo_name"], weibo_user_id=self.uid, is_used=0)
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
            weibo_user = WeiboUser(weibo_username=username, weibo_password=password, weibo_id=user["user_id"],
                                   weibo_nickname=user["user_name"], weibo_count=user["weibo_count"])
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

        return choice(weibos)

    def update_weibo(self, weibo):  # 用于转发微博后的将数据库的未转发改成已转发
        session = self.Session()
        w = session.query(WeiboDom).filter_by(mid=weibo["mid"], weibo_user_id=self.uid).first()
        w.is_forward = 1
        print("已更新数据库")
        session.commit()
        session.close()

    def get_user_id(self, username):  # uid
        session = self.Session()
        weibo_user = session.query(WeiboUser).filter_by(weibo_username=username).first()
        if not weibo_user:
            w = WeiBo(self.username, self.password)
            user_info = w.get_user_basic_info()
            print(user_info)
            if self.dom_user_info(self.username, self.password, user_info):
                print("已将微博账号信息存入数据库")
            weibo_user = session.query(WeiboUser).filter_by(weibo_username=username).first()
        uid = weibo_user.weibo_id
        return uid