from weibo import WeiBo
import random
from mythread import MyThread
import queue
from apscheduler.schedulers.blocking import BlockingScheduler
import time


w = WeiBo('15282343727', '162162162')
def dom_weibo():
    uids = w.uid_from_sqlite()
    q1 = queue.Queue()
    for uid in uids:
        q1.put(uid)
    q2 = queue.Queue()
    while not q1.empty():
        u = q1.get()
        print(u)
        t = MyThread(w.get_personal_weibo, (u,))
        t.start()
        t.join()
        for data in t.get_result():
            # print(data)
            q2.put(data)
    while not q2.empty():
        weibo = q2.get()
        # print(weibo)
        t = MyThread(w.dom_wbid, (weibo,))
        t.start()
        t.join()


def main():
    # time.sleep(10)
    sched = BlockingScheduler()
    sched.add_job(dom_weibo, 'interval', hours=2, id='dom')
    sched.add_job(w.forward_weibo_from_sql, 'interval', hours=2, minutes=5, id='forward')
    sched.start()


if __name__ == '__main__':
    main()
