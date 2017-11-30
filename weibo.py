import requests
import time
import re
import sqlite3
from bs4 import BeautifulSoup
import random


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

    def make_post_data(self, d):
        content = '@麦卖翁'
        data = {'id': d[1], 'mid': d[2], 'st': '', 'content': content}
        return data

    def uid_from_sqlite(self):
        conn = sqlite3.connect('weibo.db')
        cur = conn.cursor()
        cur.execute('SELECT uid FROM followed')
        us = cur.fetchall()
        uids = []
        for u in us:
            uids.append(u[0])
        return uids

    def get_all_weibo(self):
        '''
        # 获取该帐号下所有微博
        :return datas=(id, mid, st):
        '''
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
                datas.append((id, mid))
                # print(data)
        return datas

    def get_personal_weibo(self, uid):
        '''
        通过uid访问博主主页获取主页containerid，
        通过主页containerid获取微博containerid
        :param uid:
        :return datas:
        '''
        # st = self.get_st()
        headers = {'Host': 'm.weibo.cn',
                    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate',
                    'Referer': 'https://m.weibo.cn/',
                    'Connection': 'close',
                    'Upgrade-Insecure-Requests': '1'}
        first_containerid_url = 'https://m.weibo.cn/u/%s' % uid
        r = self.s.get(first_containerid_url, headers=headers, cookies=self.cookies)
        cookie = r.headers['Set-Cookie']
        # print(cookie)
        start = re.search('fid%3D100', cookie).span()[1] - 3
        end = re.search('fid%3D100', cookie).span()[1] + 13
        first_containerid = cookie[start:end]
        # print(first_containerid)
        params = {'type': 'uid', 'value': uid, 'containerid': first_containerid}
        # print(params)
        second_containerid_url = 'https://m.weibo.cn/api/container/getIndex'
        r2 = self.s.get(second_containerid_url, headers=headers, params=params, cookies=self.cookies)
        # print(r2.json())
        second_containerid = r2.json()['tabsInfo']['tabs'][1]['containerid']
        params['containerid'] = second_containerid
        # print(params)
        r3 = self.s.get(second_containerid_url, headers=headers, params=params, cookies=self.cookies)
        # print(r3.json())
        cards = r3.json()['cards']
        datas = []
        for card in cards:
            if card['card_type'] == 9:
                wbid = card['mblog']['id']
                mid = card['mblog']['mid']
                text = card['mblog']['text']
                content = BeautifulSoup(text, 'html.parser').text
                datas.append((uid, wbid, mid, content))
                # print(data)
        # print(datas)
        return datas

    def forward_weibo(self, data): # post_data = id='',content=''mid=''&st=''
        headers = {'Host': 'm.weibo.cn',
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Referer': 'https://m.weibo.cn',
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Connection': 'close'}
        post_data = self.make_post_data(data)
        post_data['st'] = self.get_st()
        # print(data)
        url = 'https://m.weibo.cn/api/statuses/repost'
        r = self.s.post(url, headers=headers, data=post_data, cookies=self.cookies)
        try:
            if r.json()['ok'] == 1:
                t = random.randint(60, 120)
                print('转发成功,暂停%s秒' % t)
                time.sleep(t)
                conn = sqlite3.connect('weibo.db')
                conn.execute('UPDATE weibo SET is_forward=1 WHERE wbid="%s"' % post_data['mid'])
                conn.commit()
                conn.close()
                print('已将数据更新至数据库')
                return True
            else:
                print(r.text)
                print('转发失败,暂停30秒')
                time.sleep(30)
                conn = sqlite3.connect('weibo.db')
                conn.execute('UPDATE weibo SET is_forward=1 WHERE wbid="%s"' % post_data['mid'])
                conn.commit()
                conn.close()
                print('已将数据更新至数据库')
                return None
        except:
            print('未知错误，暂停五分钟')
            time.sleep(300)

    def dom_wbid(self, data, sql):
        conn = sqlite3.connect(sql)
        cur = conn.cursor()
        try:
            cur.execute('SELECT * FROM weibo WHERE wbid = "%s"' % data[1])

            if cur.fetchone():
                print('该微博已存在于数据库')
                return None
        except:
            print(data)
        sql = 'INSERT INTO weibo (uid, wbid, mid, content, is_forward) values ("%s", "%s", "%s", "%s", %s)' %\
                (data[0], data[1], data[2], data[3], 0)
        # print(sql)
        try:
            cur.execute(sql)
            print('储存成功')
            conn.commit()
            conn.close()
            return True
        except:
            return None

    def forward_weibo_from_sql(self, sql):
        conn = sqlite3.connect(sql)
        cur = conn.cursor()
        cur.execute('SELECT * FROM weibo WHERE is_forward=0')
        weibos = cur.fetchall()
        if not weibos:
            print('没有更多数据了')
        for weibo in weibos:
            data = (weibo[1], weibo[2], weibo[3], weibo[4])
            self.forward_weibo(data)

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
        print(user[0])
        if cur.fetchone():
            print('已存在于数据库')
            return None
        try:
            cur.execute('INSERT INTO followed (uid, screen_name, description) values("%s", "%s", "%s")' % (user[0], user[1], user[2]))
            print('储存成功')
        except:
            raise
        conn.commit()
        conn.close()

    def get_others_follow_and_fans(self, uid):
        headers1 = {'Host': 'm.weibo.cn',
                    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate',
                    'Referer': 'https://m.weibo.cn/p/index?containerid=231051_-_followersrecomm_-_6034824916&luicode=10000011&lfid=1005056034824916&featurecode=20000320',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Connection': 'close'}
        headers2 = {'Host': 'm.weibo.cn',
                    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate',
                    'Referer': 'https://m.weibo.cn/p/index?containerid=231051_-_fansrecomm_-_5827525376&\
                    luicode=10000011&lfid=1005055827525376',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Connection': 'close'}
        containerid = '100505' + uid
        params = {'type': 'uid', 'value': uid, 'containerid': containerid}
        url = 'https://m.weibo.cn/api/container/getIndex'
        r = self.s.get(url, headers=headers1, params=params, cookies=self.cookies)
        # print(r.url)
        try:
            f_url = 'https://m.weibo.cn/api/container/getIndex'
            follows = re.search('\?(.*)', r.json()['userInfo']['follow_scheme']).group()
            follows_url = f_url + follows.replace('recomm', '') + '&featurecode=20000320&type=uid&value=6034824916'
            follow_count = r.json()['userInfo']['follow_count']
            fans = re.search('\?(.*)',r.json()['userInfo']['fans_scheme']).group()
            fans_url = url + fans.replace('recomm', '') + '&featurecode=20000320&type=uid&value=6034824916'
            fans_count = r.json()['userInfo']['followers_count']
            # print(r.json())
        except:
            print(r.url)
            raise
        users = []
        for i in range(1, 20):
            follow_url = follows_url
            if i == 1:
                r2 = self.s.get(follow_url, headers=headers2, cookies=self.cookies)
                try:
                    all_peopel = r2.json()['cards'][1]['card_group']
                except:
                    continue
            else:
                follow_url += '&page=' + str(i)
                r2 = self.s.get(follow_url, headers=headers2, cookies=self.cookies)
                try:
                    all_peopel = r2.json()['cards'][0]['card_group']
                except:
                    print('没有更多内容')
                    break
            print(r2.url)
            try:
                for peopel in all_peopel:
                    id = peopel['user']['id']
                    screen_name = peopel['user']['screen_name']
                    description = peopel['user']['description']
                    users.append((id, screen_name, description))
                print('关注的第%s页获取成功' % str(i))
                time.sleep(10)
            except:
                raise
        for i in range(1, 20):
            fan_url = fans_url
            if i == 1:
                r3 = self.s.get(fan_url, headers=headers2, cookies=self.cookies)
                try:
                    all_peopel = r3.json()['cards'][1]['card_group']
                except:
                    continue
            else:
                fan_url += '&since_id=' + str(i)
                r3 = self.s.get(fan_url, headers=headers2, cookies=self.cookies)
                try:
                    all_peopel = r3.json()['cards'][1]['card_group']
                except:
                    print('没有更多内容')
                    break
            print(r3.url)
            try:
                for peopel in all_peopel:
                    id = peopel['user']['id']
                    screen_name = peopel['user']['screen_name']
                    description = peopel['user']['description']
                    users.append((id, screen_name, description))
                print('粉丝的第%s页获取成功' % str(i))
                time.sleep(10)
            except:
                raise
        return users

    def get_lucky_draw_weibo(self):
        headers = {'Host': 'm.weibo.cn',
                    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'X-Requested-With': 'XMLHttpRequest',
                    "Referer": "https://m.weibo.cn/p/100103type%3D1%26q%3D%E6%8A%BD%E5%A5%96?type=all&queryVal=\
                     %E6%8A%BD%E5%A5%96&featurecode=20000320&lunicode=10000011&lfid=106003type%3D1&title=%E6%8A%\
                     BD%E5%A5%96",
                    'Connection': 'close'}
        url = 'https://m.weibo.cn/api/container/getIndex'
        params = {
            "type": "all",
            "queryVal": "微博抽奖平台",
            "featurecode": "20000320",
            "luicode": "10000011",
            "lfid": "106003type=1",
            "title": "微博抽奖平台",
            "containerid": "100103type=1&q=微博抽奖平台"}
        r = self.s.get(url, headers=headers, params=params, cookies=self.cookies)
        try:
            return r.json()
        except:
            return None

    def dom_lucky_weibo(self):
        # print(d['cards'])
        # ws = d["cards"][4]["card_group"]
        d = self.get_lucky_draw_weibo()
        if not d:
            print("未获取到可转发的微博")
            return False
        ws = []
        for w in d['cards']:
            try:
                for card in w["card_group"]:
                    ws.append(card)
            except:
                continue
        # print(len(weibos))
        weibos = []
        # print(ws)
        for weibo in ws:
            try:
                uid = weibo["mblog"]["user"]["id"]
                wbid = weibo["mblog"]["id"]
                mid = weibo["mblog"]["mid"]
                content = weibo["mblog"]["text"]
                if "微博抽奖平台" in content:
                    weibos.append((uid, wbid, mid, content))
            except:
                continue
        for wb in weibos:
            self.dom_wbid(wb, "lucky_weibo.db")
