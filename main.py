from weibo import WeiBo, WeiboHandle
from mythread import MyThread
from queue import Queue
from random import choice, randint
import time


def main():
    username = "15170307370"
    password = "lzjlzj123"
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
    contents = ["test1", "test2", "test3", "test4"]
    
    weibos = weibo_handle.get_weibo_from_database()
    if not weibos:
        print("暂无微博")
        exit
    for weibo_content in weibos:
        content = choice(contents)
        w.forward_weibo(weibo_content, content)
        weibo_handle.update_weibo(weibo_content)
        time.sleep(randint(5, 10))


if __name__ == "__main__":
    main()
    