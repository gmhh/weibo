from weibo import WeiBo
from mythread import MyThread
import queue

w = WeiBo('15170307370', 'lzjlzj123')


uids = w.uid_from_sqlite()
q1 = queue.Queue()
for uid in uids:
    users = w.get_others_follow_and_fans(uid)
    for user in users:
        q1.put(user)
    while not q1.empty():
        u = q1.get()
        t = MyThread(w.dom_followed_peopel, (u,))
        t.start()
        t.join()