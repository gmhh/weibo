from weibo import WeiBo
from weibohandle import WeiboHandle
from thread import MyThread
from queue import Queue
from apscheduler.schedulers.blocking import BlockingScheduler


username = "username"
password = "password"


def get_and_dom():
    print("cron start")
    w = WeiBo(username, password)
    weibo_handle = WeiboHandle(username)
    user_info = w.get_user_basic_info()
    if weibo_handle.dom_user_info(username, password, user_info):
        print("已将微博账号信息存入数据库")
    follows = w.get_user_follows()
    for follow in follows:
        if weibo_handle.dom_weibo_follow(follow):
            print("已将微博账号的关注信息存入数据库")
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


def forward():
    print("cron start")
    w = WeiBo(username, password)
    weibo_handle = WeiboHandle(username)
    weibo_content = weibo_handle.get_weibo_from_database()
    if not weibo_content:
        print("暂无微博")
        exit
    content = "test"  # "#食品青春# @南昌大学食品学院团委"
    result = w.forward_weibo(weibo_content, content)
    if not result:
        print("转发失败")
    weibo_handle.update_weibo(weibo_content)


def main():
    scheduler = BlockingScheduler()
    scheduler.add_job(get_and_dom, 'cron', hour='0-8', minute='0-59/20')
    scheduler.add_job(forward, 'cron', hour='9-23', minute='0-59/1')
    scheduler.start()


if __name__ == "__main__":
    main()
