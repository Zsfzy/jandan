import requests
import hashlib
import base64
import time
import re
from bs4 import BeautifulSoup

def base64_decode(str):
    missing_padding = 4 - len(str) % 4
    if missing_padding:
        str += b'='*missing_padding
    return base64.decodebytes(str)

class jiandan(object):
    def __init__(self):
        self.agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0"
        self.headers = {'User-Agent': self.agent}
        self.timeout = 10
        self.key = None

    def time(self):
        return int(str(time.time())[0:10])

    def md5(self, str):
        return hashlib.md5(str.encode('utf8')).hexdigest()

    def getKey(self, text):
        m = re.search(r'//cdn.jandan.net/static/min/\S*\d{8}\.js{1}', text)
        url = 'https:' + m.group(0)
        r = self.getData(url)
        m = re.search(r'var c=\S+\(e,"(\S+)"\);', r.text)
        self.key = m.group(1)

    def getData(self, url, headers = None, timeout = None):
        if headers == None:
            headers = self.headers
        if timeout == None:
            timeout = timeout

        try:
            r = requests.get(url, headers=headers, timeout=timeout)
        except:
            # 超时便重试
            return self.getData(url = url, headers = headers, timeout = timeout)

        if r.status_code != 200:
            print("网络异常，状态码:%d。" % (r.status_code))
            return False
        return r

    def meizi(self, page = 1):
        url = "http://jandan.net/ooxx/page-%d#comments" % (page)
        r = self.getData(url)
        if r:
            text = BeautifulSoup(r.text, 'lxml')
            img_urls = []
            for img_hash in text.find_all(class_ = 'img-hash'):
                if self.key == None:
                    self.getKey(r.text)
                img_urls.append('https:'+self.decrypt_img_hash(img_hash.get_text(), self.key))
            return img_urls
        return
        #     nextPage = text.find(class_ = 'next-comment-page')
        #     if nextPage:
        #         time.sleep(50)
        #         self.meizi(page + 1, 1)

    def decrypt_img_hash(self, m, r, d = None):
        e = 'DECODE'
        r = r if r else ''
        d = d if d else 0
        q = 4
        r = self.md5(r)
        # js的截取是从第X个位置截取x个字符字符 。而python的是从第X个位置截取到第X个位置
        o = self.md5(r[0:16])
        # n = self.md5(r[16:32])

        if q:
            if e == 'DECODE':
                l = m[0:q]
            else:
                l = ''

        c = o + hashlib.md5((o + l).encode('utf8')).hexdigest()
        if e == 'DECODE':
            m = m[q:]
            k = base64_decode(m.encode('utf8'))

        h = []
        for g in range(256):
            h.append(g)

        b = []
        for g in range(256):
            b.append(g)
            b[g] = ord(c[g % len(c)])

        f = 0
        for g in range(256):
            f = (f + h[g] + b[g]) % 256
            tmp = h[g]
            h[g] = h[f]
            h[f] = tmp

        tmp = []
        for g in k:
            tmp.append(g)
        k = tmp

        t = ''
        f = 0
        for g in range(len(k)):
            p = g
            p = (p + 1) % 256
            f = (f + h[p]) % 256
            tmp = h[p]
            h[p] = h[f]
            h[f] = tmp
            t += chr(k[g] ^ (h[(h[p] + h[f]) % 256]))

        # if e == "DECODE":
        #     if (int(t[0:10]) == 0 or int(t[0:10]) - self.time() > 0) and t[10:26] == self.md5((t[26:] + n)[0:16]):
        #         t = t[26:]
        #     else:
        #         t = ''
        t = t[26:]
        return t


def main():
    main = jiandan()
    print(main.meizi(1))
    
    pass

if __name__ == '__main__':
    main()
