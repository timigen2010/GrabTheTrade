from django.contrib.auth.models import User
from django.db import models
import lxml.html as html
from urllib.request import urlopen

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
        # for country in countries_code:
            
        page = urlopen("http://habrahabr.ru/")
        doc = html.document_fromstring(page.read())
        asvesdo = []
        for topic in doc.cssselect('h2.post__title a.post__title_link'):
            asvesdo.append(topic.text)

        return asvesdo
