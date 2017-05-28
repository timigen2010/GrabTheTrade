import django
django.setup()
from celery.task import task

import lxml.html as html
from urllib import request
from pprint import pprint
from random import choice
import re
from .models import Country, TradeInfo, DirectionType


@task(ignore_result=True, max_retries=1, default_retry_delay=10)
def countries_counting(country, countries_code, resource, language, dir_types, user_agents, proxies):
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

            elements = doc.cssselect('#ctl00_PageContent_MyGridView1 tr:nth-child(4) td[title="Direct Data"]')
            years = doc.cssselect('#ctl00_PageContent_MyGridView1 tr:nth-child(3) th a')
            temp = []
            for i in range(len(elements)):
                temp.append({
                    'country': doc.cssselect('#ctl00_NavigationControl_DropDownList_Country >'
                                             + ' option:checked')[0].text_content(),
                    'partner': doc.cssselect('#ctl00_NavigationControl_DropDownList_Partner >'
                                             + ' option:checked')[0].text_content(),
                    'dir_type': dir_type,

                    'year': years[i].text_content()[-4:],

                    'value': elements[i].text_content()
                })
            pprint(temp)

            if temp:
                country_obj, created = Country.country.get_or_create(code=temp[0]['country'])
                partner_obj, created = Country.country.get_or_create(code=temp[0]['partner'])
                dir_type_obj = DirectionType.objects.get(id=temp[0]['dir_type'])

                if country and partner and dir_type:
                    ti = TradeInfo.info.add_trade_info(resource, country_obj, partner_obj, dir_type_obj,
                                                       int(temp[0]['year']),
                                                       float(re.sub(r"[,]", "", temp[0]['value'])) * 1000, 1)
    return
