from mythread import MyThread
from weibo import WeiBo
from apscheduler.schedulers.blocking import BlockingScheduler


def forward_lucky_weibo():
    w = WeiBo('15170307370', 'lzjlzj123')
    w.dom_lucky_weibo()
    w.forward_weibo_from_sql('lucky_weibo.db')


def main():
    w = WeiBo('15170307370', 'lzjlzj123')
    sche = BlockingScheduler()
    sche.add_job(w.dom_lucky_weibo, 'interval', minutes=10, id='dom')
    sche.add_job(w.forward_weibo_from_sql,  'interval', args=('lucky_weibo.db', ),  minutes=30, id='forward')
    sche.start()


if __name__ == '__main__':
    main()