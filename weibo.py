import requests
import time
import re


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
        self.url = 'https://passport.weibo.cn/sso/login'

    def login(self):
        r = self.s.post(self.url, headers=self.login_headers, data=self.login_data)
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
        with open('%s.txt'%self.username, 'r') as f:
            cookies = {}
            for line in f.read().split(';'):
                name, value = line.strip().split('=', 1)  # 1代表只分割一次
                cookies[name] = value
            return cookies

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

    def make_data(self, data):
        content = '@南昌大学生工162团支部'
        data = {'id': data[0], 'mid': data[1], 'st': data[2], 'content': content}
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
        url = 'https://m.weibo.cn/api/statuses/repost'
        r = self.s.post(url, headers=headers, data=data, cookies=self.cookies)
        if r.json()['ok'] == 1:
            print('转发成功')
        else:
            print(r.text)
            print('转发失败')
            return None


w = WeiBo('15170307370', 'lzjlzj123')
datas = w.get_all_weibo()
for d in datas:
    data = w.make_data(d)
    time.sleep(10)
    print(data)
    w.forword_weibo(data)


