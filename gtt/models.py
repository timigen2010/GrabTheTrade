from django.contrib.auth.models import User
from django.db import models
import lxml.html as html
from urllib.request import urlopen
from urllib import request
from pprint import pprint
from django.conf import settings
from random import choice
from multiprocessing import Pool
import re


# Create your models here.


MAX_SHORT_TEXT_LENGTH = 255


class CountryManager(models.Manager):
    def add_country(self, code):
        country = self.create(code=code)
        return country


class Country(models.Model):
    code = models.CharField(max_length=255)
    country = CountryManager()


class DirectionType(models.Model):
    name = models.CharField(max_length=255)


class TemplateManager(models.Manager):
    def add_template(self, body):
        template = self.create(body=body)
        return template


class Template(models.Model):
    body = models.TextField()
    template = TemplateManager()


class ResourceManager(models.Manager):
    def add_resource(self, name, url, template):
        resource = self.create(name=name, url=url, template=template)
        return resource


class Resource(models.Model):
    name = models.CharField(max_length=255)
    url = models.TextField()
    template = models.ForeignKey(Template)
    resource = ResourceManager()


class TradeInfoManager(models.Manager):
    def add_trade_info(self, resource, country, partner, direction_type, year, value, used):
        trade_info = self.create(resource=resource, country=country, partner=partner,
                                 direction_type=direction_type, year=year, value=value, used=used)
        return trade_info


class TradeInfo(models.Model):
    resource = models.ForeignKey(Resource)
    country = models.ForeignKey(Country, related_name="trade_country")
    partner = models.ForeignKey(Country, related_name="trade_partner")
    direction_type = models.ForeignKey(DirectionType)
    year = models.IntegerField()
    value = models.FloatField()
    used = models.BooleanField(default=1)
    info = TradeInfoManager()


class Statistic(models.Model):
    country = models.ForeignKey(Country, related_name="statistic_country")
    partner = models.ForeignKey(Country, related_name="statistic_partner")
    index = models.FloatField()


class AnalyzedTradeInfo(models.Model):
    country = models.ForeignKey(Country, related_name="analyzed_trade_country")
    partner = models.ForeignKey(Country, related_name="analyzed_trade_partner")
    direction_type = models.ForeignKey(DirectionType)
    year = models.IntegerField()
    value = models.FloatField()


class Prediction(models.Model):
    analyzed_trade_info = models.ForeignKey(AnalyzedTradeInfo)
    value = models.FloatField()


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
        template = Template.template.add_template('mmm')
        template.save()
        resource = Resource.resource.add_resource('mmm', 'http://www.trademap.org/', template)
        resource.save()
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
                                                               float(re.sub(r"[,]", "", temp[-1]['value']))*1000, 1)

                        # asvesdo.append(temp)
        return asvesdo
