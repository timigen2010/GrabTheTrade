from django.contrib.auth.models import User
from django.db import models
import lxml.html as html
from urllib.request import urlopen
from urllib import request
from pprint import pprint
from django.conf import settings
from random import choice

# Create your models here.


MAX_SHORT_TEXT_LENGTH = 255


class Article(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    user = models.ForeignKey(User)

    def __str__(self):
        return self.title

    def get_short_text(self):
        if len(self.text) > MAX_SHORT_TEXT_LENGTH:
            return self.text[:MAX_SHORT_TEXT_LENGTH]
        else:
            return self.text


class Data(models.Model):
    text = models.TextField()

    @staticmethod
    def grab_the_site():
        countries_code = [x for x in range(4, 717, 1)]
        language = 1
        dir_types = [1, 2, 4]
        asvesdo = []

        user_agents = open("gtt/static/gtt/hideme/useragents.txt").read().split('\n')
        # proxies = open("gtt/static/gtt/hideme/proxies.txt").read().split('\n')
        url = "http://www.httptunnel.ge/ProxyListForFree.aspx"
        p_req = request.Request(url)
        p_page = request.urlopen(p_req)

        p_doc = html.document_fromstring(p_page.read())
        ips = p_doc.cssselect('#ctl00_ContentPlaceHolder1_GridViewNEW tr td a')
        proxies = []
        for ip in ips:
            proxies.append(ip.text_content())

        for country in countries_code:
            for partner in countries_code:
                for dir_type in dir_types:
                    url = "http://www.trademap.org/tradestat/Bilateral_TS.aspx?nvpm=" + str(language) \
                          + "|" + str(country).rjust(3, '0') + "||" \
                          + str(partner).rjust(3, '0') + "||TOTAL|||2|1|1|" \
                          + str(dir_type) + "|2|1|1|1|1"

                    try:
                        req = request.Request(url)
                        req.add_header('User-Agent', choice(user_agents))

                        page = request.urlopen(req)

                        doc = html.document_fromstring(page.read())
                        allok = 1
                        print('duple success')
                    except:
                        allok = 0
                        print('site cut')

                    while not allok:
                        try:
                            proxy = {'http': 'http://' + choice(proxies)}

                            req = request.Request(url)
                            req.add_header('User-Agent', choice(user_agents))

                            opener = request.build_opener(request.ProxyHandler(proxy))
                            request.install_opener(opener)

                            page = request.urlopen(req)

                            doc = html.document_fromstring(page.read())
                            allok = 1
                            print('new success')
                        except:
                            allok = 0
                            print('bad server error')

                    elements = doc.cssselect('#ctl00_PageContent_MyGridView1 tr:nth-child(4) td[title="Direct Data"],'
                                             + ' #ctl00_PageContent_MyGridView1 tr:nth-child(4) td[title="Mirror Data"]')
                    temp = []
                    for el in elements:
                        temp.append({
                            'country': doc.cssselect('#ctl00_NavigationControl_DropDownList_Country >'
                                                     + ' option:checked')[0].text_content(),
                            'partner': doc.cssselect('#ctl00_NavigationControl_DropDownList_Partner >'
                                                     + ' option:checked')[0].text_content(),
                            'dir_type': 1,
                            'value': el.text_content()
                        })
                    pprint(temp)
                    # asvesdo.append(temp)
        return asvesdo
