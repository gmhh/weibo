from weibo import WeiBo
from weibohandle import WeiboHandle
from thread import MyThread
from queue import Queue
from apscheduler.schedulers.blocking import BlockingScheduler
from random import randint
from origin import *
import os


class time_deal():
    def __init__(self, username, password):
        self.username = username
        self.password = password
        # self.w = WeiBo(username, password)
        # self.weibo_handle = WeiboHandle(username, password)

    def get_and_dom(self):
        # print("cron start")
        # follows = self.w.get_user_follows()
        # for follow in follows:
        #    if self.weibo_handle.dom_weibo_follow(follow):
        #        print("已将微博账号的关注信息存入数据库")
        print("getting weibo from follows")
        w = WeiBo(self.username, self.password)
        weibo_handle = WeiboHandle(self.username, self.password)
        uids = weibo_handle.get_followed_from_database()
        q1 = Queue()
        q2 = Queue()
        for uid in uids:
            q1.put(uid)
        while not q1.empty():
            uid = q1.get()
            t = MyThread(func=w.get_user_weibo, args=(uid,))
            t.start()
            t.join()
            for data in t.get_result():
                q2.put(data)
        while not q2.empty():
            weibo = q2.get()
            t = MyThread(func=weibo_handle.dom_weibo, args=(weibo,))
            t.start()
            t.join()
        
    def forward(self):
        print("cron start")
        w = WeiBo(self.username, self.password)
        weibo_handle = WeiboHandle(self.username, self.password)
        weibo_content = weibo_handle.get_weibo_from_database()
        if not weibo_content:
            print("暂无微博")
            self.get_and_dom()
        content = "#食品青春# @南昌大学食品学院团委 @南昌大学食品学院学生会"
        result = w.forward_weibo(weibo_content, content)
        if not result:
            print("转发失败")
        weibo_handle.update_weibo(weibo_content)

    def send_origin(self, mod_class_name, mod, pic_name):
        print("cron start")
        w = WeiBo(self.username, self.password)
        m = mod_class_name(mod, pic_name)
        content = m.make_content()
        pic_id = w.upload_pic("pic/%s.jpg" % pic_name)
        w.original_weibo(content, pic_id)

def main():
    weibo_username = os.getenv("weibo_username") or "15282343727"
    weibo_password = os.getenv("weibo_password") or "162162162"
    t = time_deal(weibo_username, weibo_password)
    m = '0-59/' + str(randint(5,10))
    scheduler = BlockingScheduler()
    scheduler.add_job(t.get_and_dom, 'cron', hour='0-6', minute='0-59/20')  # 储存
    scheduler.add_job(t.forward, 'cron', hour='0-23/2', minute=m)  # 转发
    scheduler.add_job(t.send_origin, 'cron', args=(one_word, "一言", "one_word"), hour=8, minute=1)  # 一言
    scheduler.add_job(t.send_origin, 'cron', args=(get_weather, "天气", "weather"), hour=6, minute=1)  # 天气
    scheduler.add_job(t.send_origin, 'cron', args=(mie_word, "咩语", "mie_word"), hour=22, minute=1)  # 咩语
    scheduler.add_job(t.send_origin, 'cron', args=(recommend_food, "美食推荐", "food"), hour=11, minute=1)  # 美食推荐
    scheduler.add_job(t.send_origin, 'cron', args=(daily_news, "每日国际视野", "news"), hour=9, minute=1)  # 每日国际视野
    scheduler.add_job(t.send_origin, 'cron', args=(history_of_today, "历史上的今天", "history"), hour=10, minute=1)  # 历史上的今天
    scheduler.start()


if __name__ == "__main__":
    main()
