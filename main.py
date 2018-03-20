from weibo import WeiBo
from weibohandle import WeiboHandle
from thread import MyThread
from queue import Queue
from apscheduler.schedulers.blocking import BlockingScheduler
from one_word import weibo_extend
from random import randint


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
        content = "#食品青春# @南昌大学食品学院团委"
        result = w.forward_weibo(weibo_content, content)
        if not result:
            print("转发失败")
        weibo_handle.update_weibo(weibo_content)

    def make_weibo(self):
        print("cron start")
        w = WeiBo(self.username, self.password)
        c = weibo_extend.get_one_word()
        content = "#食品青春#【一言】" + c + "@南昌大学食品学院团委"
        if weibo_extend.get_weibo_pic():
            pic_id = w.upload_pic("pic/mie_word.jpg")
        w.original_weibo(content, pic_id)
    
    def good_moring_evening(self, moring=True):
        print("cron start")
        w  = WeiBo(self.username, self.password)
        weather = weibo_extend.get_weather()
        if moring:
            content = "#食品青春#【天气】早安！今天" + weather + " @南昌大学食品学院团委"
        else:
            content = "#食品青春#【天气】晚安！" + " @南昌大学食品学院团委"
        if weibo_extend.get_weibo_pic():
            pic_id = w.upload_pic("pic/mie_word.jpg")
        w.original_weibo(content, pic_id)


    def mie_word(self):
        w = WeiBo(self.username, self.password)
        c = weibo_extend.get_mie_word()
        content = "#食品青春#" + c + "  --《咩语》" + " @南昌大学食品学院团委"
        if weibo_extend.get_weibo_pic():
            pic_id = w.upload_pic("pic/mie_word.jpg")
        w.original_weibo(content, pic_id)

    def food(self):
        print("cron start")
        w = WeiBo(self.username, self.password)
        c = weibo_extend.get_food_from_database()
        content = "#食品青春#【美食推荐】" + c + "  @南昌大学食品学院团委"
        pic_id = w.upload_pic("pic/food.jpg")
        w.original_weibo(content, pic_id)

def main():
    t = time_deal("15282343727", "162162162")
    m = '0-59/' + str(randint(5,10))
    scheduler = BlockingScheduler()
    # scheduler.add_job(t.get_and_dom, 'cron', hour='0-6', minute='0-59/20')  # 储存
    scheduler.add_job(t.forward, 'cron', hour='0-23/2', minute=m)  # 转发
    scheduler.add_job(t.make_weibo, 'cron', hour=10, minute=20)  # 一言
    scheduler.add_job(t.good_moring_evening, 'cron', args=(True, ), hour=6, minute=1) # 早安
    scheduler.add_job(t.good_moring_evening, 'cron', args=(False, ), hour=22, minute=1) # 晚安
    scheduler.add_job(t.mie_word, 'cron',hour=21, minute=17)  # 咩语
    scheduler.add_job(t.food, 'cron', hour=11, minute=1) #美食推荐
    scheduler.start()


if __name__ == "__main__":
    main()
