from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout as logout_f, authenticate, login as login_f
from django.http import JsonResponse
from querystring_parser import parser
from celery.result import AsyncResult
from datetime import datetime
import json




# Create your views here.
from gtt.models import Article, Data, Resource, Template, Task


def process_status_by_resource(resource):
    tasks = Task.task.filter(resource__exact=resource).order_by('-date_start')[:10]
    if tasks:
        return processes_status(tasks, True)
    else:
        return []


def processes_status(tasks, return_all_task=False):
    tasks_status = []
    for task in tasks:
        bodys = json.loads(task.body)
        count_success = 0
        for task_id in bodys:
            tsk = AsyncResult(task_id)
            if tsk.status == 'SUCCESS':
                count_success += 1
        status = count_success*100//len(bodys)
        if return_all_task:
            tasks_status.append({'task': task, 'status': status})
        else:
            tasks_status.append({'task': task.id, 'status': status})
    return tasks_status


def home(request):
    articles = Article.objects.all()
    context = {
        'articles': articles
    }
    return render(request, 'gtt/home.html', context)


def article(request, article_id):
    founded_article = get_object_or_404(Article, id=article_id)
    return render(request, 'gtt/article.html', {'article': founded_article})


def parsing(request):
    resource = Resource.resource.filter(id__exact=request.POST['id'])
    if resource:
        data = Data()
        data.grab_the_site(resource[0])
        return JsonResponse(0, safe=False)
    else:
        return JsonResponse(1, safe=False)


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
                         post_data['partner_css'], post_data['year_css'], post_data['direction_css'],
                         post_data['value_css'], post_data['factor']]
        template = Template.template.add_template(json.dumps(template_data))
        template.save()
        resource = Resource.resource.add_resource(post_data['resource_name'], post_data['url'], template)
        resource.save()
        return JsonResponse({'id': resource.id, 'name': resource.name}, safe=False)
    else:
        return HttpResponse(status=404)


def get_resource(request):
    if request.user.is_authenticated():
        post_data = parser.parse(request.POST.urlencode())
        try:
            res = Resource.resource.get(id=post_data['id'])
        except Resource.DoesNotExist:
            return JsonResponse(False, safe=False)
        else:
            result = {"name": res.name,
                      "url": res.url,
                      "data": json.loads(res.template.body)}
            return JsonResponse(result, safe=False)
    else:
        return HttpResponse(status=404)


def edit_resource(request):
    if request.user.is_authenticated():
        post_data = parser.parse(request.POST.urlencode())
        try:
            res = Resource.resource.get(id=post_data['id'])
            template_data = [post_data['parameters'] if 'parameters' in post_data.keys() else '',
                             post_data['country_css'],
                             post_data['partner_css'], post_data['year_css'], post_data['direction_css'],
                             post_data['value_css'], post_data['factor']]
            res.template.body = json.dumps(template_data)
            res.template.save()
            res.name = post_data['resource_name']
            res.url = post_data['url']
            res.save()
        except Resource.DoesNotExist:
            return JsonResponse(False, safe=False)
        else:
            return JsonResponse(res.name, safe=False)
    else:
        return HttpResponse(status=404)


def delete_resource(request):
    if request.user.is_authenticated():
        post_data = parser.parse(request.POST.urlencode())
        try:
            res = Resource.resource.get(id=post_data['id'])
            res.template.delete()
        except Resource.DoesNotExist:
            return JsonResponse(False, safe=False)
        else:
            return JsonResponse(True, safe=False)
    else:
        return HttpResponse(status=404)


def operations(request):
    if request.user.is_authenticated():
        username = request.user.get_full_name()
        registered_date = request.user.date_joined.strftime("%d.%m.%Y %H:%M")
        res = Resource.resource.order_by('-id')
        tasks = Task.task.order_by('-date_start')[:10]
        # tasks_statuses = processes_status(tasks)
        return render(request, 'gtt/admin/operations.html', {'username': username, 'registered_date': registered_date,
                                                             'resources': res, 'tasks': tasks})
    else:
        return HttpResponse(status=404)


def tasks_statuses_by_resource(request):
    if request.user.is_authenticated():
        resource = Resource.resource.filter(id__exact=request.POST['id'])
        tasks_result = []
        if resource:
            tasks = Task.task.filter(resource__exact=resource).order_by('-date_start')[:10]
            for task in tasks:
                tasks_result.append({
                    'id': task.id,
                    'name': task.name,
                    'date_start': datetime.strftime(task.date_start, "%d.%m.%Y %H:%M"),
                    'date_end': datetime.strftime(task.date_end, "%d.%m.%Y %H:%M") if task.date_end else [],
                    'resource_name': task.resource.name
                })

        return JsonResponse(tasks_result, safe=False)
    else:
        return HttpResponse(status=404)


def get_tasks_statuses(request):
    if request.user.is_authenticated():
        tasks_ids = json.loads(request.POST['ids'])
        tasks = Task.task.filter(id__in=tasks_ids)
        statuses = []
        if tasks:
            statuses = processes_status(tasks)
        return JsonResponse(statuses, safe=False)
    else:
        return HttpResponse(status=404)




# def get_operations
