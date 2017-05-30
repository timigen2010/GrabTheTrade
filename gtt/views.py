from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout as logout_f, authenticate, login as login_f
from django.http import JsonResponse
from querystring_parser import parser
import json



# Create your views here.
from gtt.models import Article, Data, Resource, Template


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
    data = Data()
    result = data.grab_the_site()
    return render(request, 'gtt/home.html', {'data': result})


def admin(request):
    if request.user.is_authenticated():
        username = request.user.get_full_name()
        registered_date = request.user.date_joined.strftime("%d.%m.%Y %H:%M")
        return render(request, 'gtt/admin/index.html', {'username': username, 'registered_date': registered_date})
    else:
        return render(request, 'gtt/admin/login.html')


def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login_f(request, user)
            return redirect('admin')
        else:
            return render(request, 'gtt/admin/login.html')
            # Return a 'disabled account' error message
    else:
        return render(request, 'gtt/admin/login.html')
# Return an 'invalid login' error message.


def logout(request):
    logout_f(request)
    return redirect('admin')


def resources(request):
    if request.user.is_authenticated():
        username = request.user.get_full_name()
        registered_date = request.user.date_joined.strftime("%d.%m.%Y %H:%M")
        res = Resource.resource.order_by('-id')
        return render(request, 'gtt/admin/resources.html', {'username': username, 'registered_date': registered_date,
                                                            'resources': res})
    else:
        return HttpResponse(status=404)


def add_resource(request):
    if request.user.is_authenticated():
        post_data = parser.parse(request.POST.urlencode())
        template_data = [post_data['parameters'] if 'parameters' in post_data.keys() else '', post_data['country_css'],
                         post_data['partner_css'], post_data['year_css'], post_data['direction_css']]
        template = Template.template.add_template(json.dumps(template_data))
        template.save()
        resource = Resource.resource.add_resource(post_data['resource_name'], post_data['url'], template)
        resource.save()
        return JsonResponse({'id': resource.id, 'name': resource.name}, safe=False)
    else:
        return HttpResponse(status=404)
