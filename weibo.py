import requests
import time
import re
import sqlite3


class WeiBo(object):
    def __init__(self, username, password):
        self.s = requests.session()
        self.login_headers = {'Host': 'passport.weibo.cn',
                    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0',
                    'Accept': '*/*',
                    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate',
                    'Referer': 'https://passport.weibo.cn/signin/login?entry=mweibo&res=wel&wm=3349&r=http%3A%2F%2Fm.\
                    weibo.cn%2F',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Content-Length': '174',
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
        # self.url = 'https://passport.weibo.cn/sso/login'
        self.uid = ['6034824916']

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
        f = open('%s.txt' % self.username, 'w')
        f.write(cookie)
        print('cookie保存成功')
        f.close()

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
        headers = {'Host': 'm.weibo.cn',
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Referer': 'https://m.weibo.cn',
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Connection': 'close'}
        url = 'https://m.weibo.cn'
        # params = {'t': str(int(time.time()))}
        r = self.s.get(url, headers=headers, cookies=cookies)
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

    def get_st(self): # st是转发微博必要的参数,在get m.weibo.cn后返回
        headers = {'Host': 'm.weibo.cn',
                    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'close',
                    'Upgrade-Insecure-Requests': '1'}
        url = 'https://m.weibo.cn/compose/repost'
        # params = {'id': id}
        r = self.s.get(url, headers=headers, cookies=self.cookies)
        # print(r.text)
        # print(re.search(r'st:', r.text))
        start = re.search(r'st:', r.text).span()[1] + 2
        end = re.search(r'st:', r.text).span()[1] + 8
        st = r.text[start:end]
        return st

    def get_all_weibo(self):
        st = self.get_st()
        headers = {'Host': 'm.weibo.cn',
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Referer': 'https://m.weibo.cn',
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Connection': 'close'}
        url = 'https://m.weibo.cn/feed/friends'
        params = {'version': 'v4'}
        r = self.s.get(url, headers=headers, params=params, cookies=self.cookies)
        weibos = r.json()[0]
        datas = []
        for weibo in weibos['card_group']:
            # print(weibo)
            try:
                weibo['card_type']
            except:
                continue
            if weibo['card_type'] == 9:
                id = weibo['mblog']['id']
                mid = weibo['mblog']['mid']
                datas.append((id, mid, st))
                # print(data)
        return datas

    def get_personal_weibo(self, uid):
        '''
        通过uid访问博主主页获取主页containerid，
        通过主页containerid获取微博containerid
        :param uid:
        :return datas:
        '''
        st = self.get_st()
        headers = {'Host': 'm.weibo.cn',
                    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate',
                    'Referer': 'https://m.weibo.cn/',
                    'Connection': 'close',
                    'Upgrade-Insecure-Requests': '1'}
        first_containerid_url = 'https://m.weibo.cn/u/%s' %uid
        r = self.s.get(first_containerid_url, headers=headers, cookies=self.cookies)
        cookie = r.headers['Set-Cookie']
        start = re.search('fid', cookie).span()[1] + 3
        end = re.search('fid', cookie).span()[1] + 19
        containerid = cookie[start:end]
        params = {'type': 'uid', 'value': uid, 'containerid': containerid}
        second_containerid_url = 'https://m.weibo.cn/api/container/getIndex'
        r2 = self.s.get(second_containerid_url, headers=headers, params=params, cookies=self.cookies)
        containerid = r2.json()['tabsInfo']['tabs'][1]['containerid']
        params['containerid'] = containerid
        r3 = self.s.get(second_containerid_url, headers=headers, params=params, cookies=self.cookies)
        # print(r3.json())
        cards = r3.json()['cards']
        datas = []
        for card in cards:
            if card['card_type'] == 9:
                id = card['mblog']['id']
                mid = card['mblog']['mid']
                content = card['mblog']['text']
                datas.append((uid, id, mid, st, content))
                # print(data)
        return datas

    def make_data(self, data):
        content = '#食品青春#@南昌大学生工162团支部~测试测试~'
        data = {'id': data[1], 'mid': data[2], 'st': data[3], 'content': content}
        return data

    def forword_weibo(self, data): # data = id='',content=''mid=''&st=''
        headers = {'Host': 'm.weibo.cn',
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Referer': 'https://m.weibo.cn',
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Connection': 'close'}
        data = self.make_data(data)
        # print(data)
        url = 'https://m.weibo.cn/api/statuses/repost'
        r = self.s.post(url, headers=headers, data=data, cookies=self.cookies)
        if r.json()['ok'] == 1:
            print('转发成功')
        else:
            print(r.text)
            print('转发失败')
            return None

    def dom_wbid(self, data):
        conn = sqlite3.connect('weibo.db')
        cur = conn.cursor()
        cur.execute('SELECT * FROM weibo WHERE wbid = "%s" ' % data[1])
        if cur.fetchone():
            print('该微博已存在于数据库')
            return None
        sql = 'INSERT INTO weibo (uid, wbid, mid) values ("%s", "%s", "%s")' %\
                (data[0], data[1], data[2])
        # print(sql)
        cur.execute(sql)
        print('储存成功')
        conn.commit()
        conn.close()
        return True

    def get_containerid(self):
        headers = {'Host': 'm.weibo.cn',
                    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate',
                    'Referer': 'https://m.weibo.cn/',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Connection': 'close'}
        url = 'https://m.weibo.cn/home/me'
        params = {'format': 'cards'}
        r = self.s.get(url, headers=headers, params=params, cookies=self.cookies)
        t = r.json()[0]
        cards = t['card_group']
        # print(cards)
        for card in cards:
            # print(card)
            if card['card_type'] == 2:
                apps = card['apps']
                for app in apps:
                    if app['title'] == '关注':
                        containerid_url = app['scheme']
                        containerid = containerid_url[22:38]
                        return containerid

    def get_followed_people(self):
        '''
        get关注列表，返回我的关注列表
        :return followeds:
        '''
        containerid = self.get_containerid()
        headers = {'Host': 'm.weibo.cn',
                    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate',
                    'Referer': 'https://m.weibo.cn/p/second?containerid=%s_-_FOLLOWERS' % containerid,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Connection': 'close'}
        url = 'https://m.weibo.cn/api/container/getSecond'
        params = {'containerid': '%s_-_FOLLOWERS' % containerid}
        r = self.s.get(url, headers=headers,params=params, cookies=self.cookies)
        users = []
        # print(r.json())
        followed_count = r.json()['count']
        for i in range(1, int(((followed_count-1)/10))+2):
            params = {'containerid': '%s_-_FOLLOWERS' % containerid, 'page': i}
            r = self.s.get(url, headers=headers, params=params, cookies=self.cookies)
            all_peopel = r.json()['cards']
            for peopel in all_peopel:
                id = peopel['user']['id']
                screen_name = peopel['user']['screen_name']
                users.append((id, screen_name))
        return users

    def dom_followed_peopel(self, user): # user=(uid, screen_name)
        conn = sqlite3.connect('weibo.db')
        cur = conn.cursor()
        cur.execute('SELECT * FROM followed WHERE uid = "%s"' % user[0])
        if cur.fetchone():
            print('已存在于数据库')
            return None
        cur.execute('INSERT INTO followed (uid, screen_name) values("%s", "%s")' % (user[0], user[1]))
        print('储存成功')
        conn.commit()
        conn.close()


if __name__ == '__main__':
    w = WeiBo('15170307370', 'lzjlzj123')
    '''users = w.get_followed_people()
    for user in users:
        w.dom_followed_peopel(user)'''
    datas = w.get_personal_weibo('6034824916')
    for data in datas:
        if w.dom_wbid(data):
            w.forword_weibo(data)
            time.sleep(5)



