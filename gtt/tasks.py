import django
django.setup()
from celery.task import task

import lxml.html as html
from urllib import request
from pprint import pprint
from random import choice
import re
from .models import Country, TradeInfo, DirectionType, AnalyzedTradeInfo


@task(max_retries=1, default_retry_delay=10)
def parse(resource, user_agents, proxies, params, csss):

    if isinstance(params, list):
        for param in params:
            url_parts = re.split('%s|%p|%S|%P', resource.url)
            url = ""
            for i in range(len(url_parts)-1):
                url += url_parts[i] + param[i]
            url += url_parts[-1]

            try:
                req = request.Request(url)
                req.add_header('User-Agent', choice(user_agents))

                page = request.urlopen(req)

                doc = html.document_fromstring(page.read())
                allok = 1
                # print('duple success')
            except:
                allok = 0
                # print('site cut')

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
                    # print('new success')
                except:
                    allok = 0
                    # print('bad server error')

            elements = doc.cssselect(csss['value'])
            years = doc.cssselect(csss['year'])
            temp = []
            r_dir = re.compile(r'import|export|re-export', re.I)
            r_year = re.compile(r'\d\d\d\d', re.I)
            try:
                for i in range(len(elements)):
                    temp.append({
                        'country': doc.cssselect(csss['country'])[0].text_content(),
                        'partner': doc.cssselect(csss['partner'])[0].text_content(),
                        'dir_type': r_dir.search(doc.cssselect(csss['direction_type'])[0].text_content()).group(0),
                        'year': r_year.search(years[i].text_content()).group(0),
                        'value': elements[i].text_content()
                    })
                    print(temp[-1])
            except:
                True

            if temp:
                for i in range(len(temp)):
                    country_obj = Country.country.filter(code__iexact=temp[i]['country'])
                    if country_obj:
                        country_obj = country_obj[0]
                    partner_obj = Country.country.filter(code__iexact=temp[i]['partner'])
                    if partner_obj:
                        partner_obj = partner_obj[0]
                    dir_type_obj = DirectionType.objects.filter(name__iexact=temp[i]['dir_type'])
                    if dir_type_obj:
                        dir_type_obj = dir_type_obj[0]

                    if country_obj and partner_obj and dir_type_obj:
                        ti = TradeInfo.info.filter(resource__exact=resource).filter(country__exact=country_obj).filter(direction_type__exact=dir_type_obj).filter(year__exact=int(temp[i]['year']))
                        if not ti:
                            ti = TradeInfo.info.add_trade_info(resource, country_obj, partner_obj, dir_type_obj,
                                                               int(temp[i]['year']),
                                                               float(re.sub(r"[,]", "", temp[i]['value']))*int(csss['factor']), 0)
                            ti.save()
                        else:
                            ti[0].value = float(re.sub(r"[,]", "", temp[i]['value']))*int(csss['factor'])
                            ti[0].used = 0
                            ti[0].save()
    return


# Проверка согласованности по коэфициенту вариации
@task(max_retries=1, default_retry_delay=10)
def analyze(resource):
    non_analyzed_trade_info = TradeInfo.info.filter(resource__exact=resource).filter(used__exact=0)
    if non_analyzed_trade_info:
        for info in non_analyzed_trade_info:
            analyzed_trade_info = TradeInfo.info.filter(year__exact=info.year).filter(country__exact=info.country).\
                filter(direction_type=info.direction_type).filter(partner__exact=info.partner).filter(used__exact=1)
            if not analyzed_trade_info:
                info.used = 1
                info.save()
            else:
                data = [float(x.value) for x in analyzed_trade_info]
                data.append(float(info.value))
                m = float(sum(data))/len(data)
                disp = sum([pow(x-m, 2) for x in data])/(len(data)-1)
                sq_disp = pow(disp, 1/2)
                v = sq_disp/m if m!=0 else 0
                if v <= 0.25:
                    info.used = 1
                    info.save()
    return


# Вычисление объединенного значения по среднему геометрическому
@task(max_retries=1, default_retry_delay=10)
def unite(resource):
    trade_info = TradeInfo.info.filter(resource__exact=resource).filter(used__exact=1)
    if trade_info:
        for info in trade_info:
            datas = TradeInfo.info.filter(year__exact=info.year).filter(country__exact=info.country).\
                filter(direction_type=info.direction_type).filter(partner__exact=info.partner).filter(used__exact=1)
            p = 1.0
            for data in datas:
                p *= float(data.value)
            p = pow(p, 1/len(datas))
            try:
                ati = AnalyzedTradeInfo.info.add_analyzed_trade_info(info.country, info.partner, info.direction_type
                                                                     , info.year, p)
                ati.save()
            except:
                ati = AnalyzedTradeInfo.info.filter(year__exact=info.year).filter(country__exact=info.country). \
                    filter(direction_type=info.direction_type).filter(partner__exact=info.partner)[0]
                ati.value = p
                ati.save()

    return
