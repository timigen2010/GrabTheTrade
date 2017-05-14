from django.contrib.auth.models import User
from django.db import models
import lxml.html as html
from urllib.request import urlopen
from pprint import pprint
import time

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
        countries_code = [x for x in range(4, 717, 4)]
        language = 1
        dir_types = [1, 2, 4]
        asvesdo = []
        # page = urlopen("http://www.trademap.org/tradestat/Bilateral_TS.aspx?nvpm=" + str(language)
        #                + "|381||008||TOTAL|||2|1|1|"
        #                + str(1) + "|2|1|1|1|1")
        # doc = html.document_fromstring(page.read())
        # ctl00_PageContent_MyGridView1 > tbody > tr:nth-child(4) > td:nth-child(5)

        # pprint(asvesdo[0]['value'])
        for country in countries_code:
            for partner in countries_code:
                for dir_type in dir_types:
                    page = urlopen("http://www.trademap.org/tradestat/Bilateral_TS.aspx?nvpm=" + str(language)
                                   + "|" + str(country).rjust(3, '0') + "||"
                                   + str(partner).rjust(3, '0') + "||TOTAL|||2|1|1|"
                                   + str(dir_type)+"|2|1|1|1|1")
                    doc = html.document_fromstring(page.read())
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
                    asvesdo.append(temp)
                    time.sleep(1)
        return asvesdo
