from django.contrib.auth.models import User
from django.db import models
import lxml.html as html
from urllib.request import urlopen
from urllib import request
from pprint import pprint
from django.conf import settings
from random import choice
import re
from multiprocessing import Pool
from itertools import repeat
import json
from itertools import product
from datetime import datetime
import time




# Create your models here.


MAX_SHORT_TEXT_LENGTH = 255


class CountryManager(models.Manager):
    def add_country(self, code, rus=None):
        country = self.create(code=code, rus=rus)
        return country


class Country(models.Model):
    code = models.CharField(max_length=255)
    rus = models.CharField(max_length=255, null=True)
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
    used = models.BooleanField(default=0)
    info = TradeInfoManager()


class TaskManager(models.Manager):
    def add_task(self, name, resource, body, date_start, date_end=None):
        task = self.create(name=name, resource=resource, body=body, date_start=date_start, date_end=date_end)
        return task


class Task(models.Model):
    name = models.CharField(max_length=255)
    resource = models.ForeignKey(Resource)
    body = models.TextField()
    date_start = models.DateTimeField()
    date_end = models.DateTimeField(null=True)
    task = TaskManager()


class Statistic(models.Model):
    country = models.ForeignKey(Country, related_name="statistic_country")
    partner = models.ForeignKey(Country, related_name="statistic_partner")
    index = models.FloatField()


class AnalyzedTradeInfoManager(models.Manager):
    def add_analyzed_trade_info(self,  country, partner, direction_type, year, value):
        analyzed_trade_info = self.create(country=country, partner=partner,
                                          direction_type=direction_type, year=year, value=value)
        return analyzed_trade_info


class AnalyzedTradeInfo(models.Model):
    country = models.ForeignKey(Country, related_name="analyzed_trade_country")
    partner = models.ForeignKey(Country, related_name="analyzed_trade_partner")
    direction_type = models.ForeignKey(DirectionType)
    year = models.IntegerField()
    value = models.FloatField()
    info = AnalyzedTradeInfoManager()

    class Meta:
        unique_together = (('country', 'partner', 'direction_type', 'year'),)


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


    def grab_the_site(self, resource):
        from .tasks import parse, analyze, unite

        # Получение ресурса и шаблона из базы
        # resource = Resource.resource.get(id=132)
        template = resource.template

        # Обработка тела шаблона, формаирование параметров
        body = json.loads(template.body)

        params = []
        if isinstance(body[0], dict):
            for param in body[0]:
                if isinstance(body[0][param], list):
                    par = [int(x) for x in body[0][param]]

                    x1, x2, x3 = par[0], par[1], par[2]
                    if [x for x in range(x1, x2, x3)]:
                        params.append([x for x in range(x1, x2, x3)])
                    else:
                        if x1 > x2:
                            params.append([x for x in range(x1, x2, -1)])

                        elif x1 < x2:
                            params.append([x for x in range(x1, x2, 1)])

                        else:
                            params.append([x1])

                else:
                    params.append(body[0][param].strip().replace(' ', '').split(","))
        csss = {
            'country': body[1],
            'partner': body[2],
            'year': body[3],
            'direction_type': body[4],
            'value': body[5],
            'factor': body[6]
        }

        # Получение списка User-Agents и Proxy
        user_agents = open("gtt/static/gtt/hideme/useragents.txt").read().split('\n')
        url = "http://www.httptunnel.ge/ProxyListForFree.aspx"
        p_req = request.Request(url)
        p_page = request.urlopen(p_req)

        p_doc = html.document_fromstring(p_page.read())
        ips = p_doc.cssselect('#ctl00_ContentPlaceHolder1_GridViewNEW tr td a')
        proxies = []
        for ip in ips:
            proxies.append(ip.text_content())

        # Выполнение парсинга
        products = list(product(*params))
        # print(params)
        maxlen = len(products)

        if maxlen > 3500000:
            return 1
        steps = []
        regulators = []
        if maxlen <= 1000:
            for p in products:
                step_el = parse.delay(resource, user_agents, proxies, p, csss)
                steps.append(step_el.id)
                regulators.append(step_el)
            task = Task.task.add_task("Парсинг", resource, json.dumps(steps), datetime.now())
            task.save()

        else:
            step = maxlen / 20000
            for x in range(2):
                print(x)
                step_el = parse.delay(resource, user_agents, proxies, products[int(x*step):int((x+1)*step+1)], csss)
                steps.append(step_el.id)
                regulators.append(step_el)
            task = Task.task.add_task("Парсинг", resource, json.dumps(steps), datetime.now(), None)
            task.save()


        while regulators:
            regulator = regulators.pop(0)
            if regulator.status != 'SUCCESS':
                regulators.append(regulator)

        task.date_end = datetime.now()
        task.save()

        # Анализ достоверности
        analyzer = analyze.delay(resource)

        task = Task.task.add_task("Анализ достоверности", resource, json.dumps([analyzer.id]), datetime.now(), None)
        task.save()

        while analyzer.status != 'SUCCESS':
            time.sleep(1)

        task.date_end = datetime.now()
        task.save()

        # Объединение данных
        unite = unite.delay(resource)

        task = Task.task.add_task("Объединение данных", resource, json.dumps([unite.id]), datetime.now(), None)
        task.save()

        while unite.status != 'SUCCESS':
            time.sleep(1)

        task.date_end = datetime.now()
        task.save()

        return 0





