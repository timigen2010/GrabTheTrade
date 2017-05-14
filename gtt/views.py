from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

# Create your views here.
from gtt.models import Article, Data


def home(request):
    articles = Article.objects.all()
    context = {
        'articles': articles
    }
    return render(request, 'gtt/home.html', context)


def article(request, article_id):
    founded_article = get_object_or_404(Article, id=article_id)
    return render(request, 'gtt/article.html', {'article': founded_article})


def data(request):
    result = Data.grab_the_site()
    return render(request, 'gtt/home.html', {'data': result})

