import requests
import bs4
import time
import getpass
import os

USERNAME = input('mssv: ')
PASSWORD = getpass.getpass('password: ')
SCORE = input('mấy sao: ')


def main():
    bot = RequestsBot(USERNAME, PASSWORD, SCORE)
    bot.login()
    bot.review()


class RequestsBot:
    def __init__(self, username, password, score):
        self.username = username
        self.password = password
        self.score = score
        self.headers = self._get_header()
        self.info = self._get_info()
        self.session = requests.session()
        self.homepage = None
        self.error = False

    def _get_header(self):
        d = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
             'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0',
             'Accept-Encoding': 'gzip,deflate',
             'Accept-Language': 'en-US,vi;q=0.7,en;q=0.3'}

        # detect os
        if os.name is not 'posix':
            d['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0'
        return d

    def _get_info(self):
        return ['lblTenGiangVien', 'lblTenMonHoc', 'lblNhom', 'lblTo']

    def login(self):
        try:
            url = 'http://teaching-quality-survey.tdt.edu.vn/stdlogin.aspx'
            login_page = self.session.get(url, headers=self.headers)
            payload = self._get_all_tag(self._get_soup(login_page), 'input')
            payload['txtUser'] = self.username
            payload['txtPass'] = self.password
            self.homepage = self.session.post(url, data=payload)
        except:
            # instantly quit, avoid error
            self.error = True

    def _get_all_tag(self, soup, tag):
        d = {}
        for t in soup.find_all(tag):
            d[t.get('name')] = t.get('value')
        return d

    def _get_soup(self, page):
        return bs4.BeautifulSoup(page.text, 'lxml')

    def review(self):
        gv_list = self._get_review_list()
        if not self.error:
            for gv in gv_list:
                self._review(gv)
        else:
            print('review failed')

    def _get_review_list(self):
        def extract_href(href):
            # dont sure how they work
            arr = href.split('(')[1].split(',')
            arr[0] = arr[0].split('\'')[1]
            arr[1] = arr[1].split('\'')[1]
            return arr

        review_soup = self._get_soup(self.homepage)
        data = [a.get('href')
                for a in review_soup.find_all('a') if a.get('href') != '']
        review_list = [extract_href(href) for href in data]
        return review_list

    def _review(self, gv):
        def set_score(d, score):
            for item in d:
                if item.__contains__('gv'):
                    d[item] = score

        def print_logs(soup, info):
            for i in info:
                s = soup.find('span', id=i)
                if s is not None:
                    print(s.text + '\t', end='')
            print('done')

        soup = self._get_soup(self.homepage)
        payload = self._get_all_tag(soup, 'input')
        payload['__EVENTTARGET'] = gv[0]
        payload['__EVENTARGUMENT'] = gv[1]
        # enter the review page
        r = self.session.post(url=self.homepage.url,
                              data=payload, headers=self.headers)
        soup = self._get_soup(r)
        payload = self._get_all_tag(soup, 'input')
        set_score(payload, self.score)
        # set coordinates for button - thật ra nó là hình đéo phải button
        payload['btnTiepTuc.x'] = '1'
        payload['btnTiepTuc.y'] = '1'
        # exit the review page
        r = self.session.post(url=r.url, data=payload, headers=self.headers)
        print_logs(soup, self.info)


if __name__ == "__main__":
    t = time.time()
    main()
    print('finished in ' + str(time.time() - t) + ' secs')
