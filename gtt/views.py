from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout as logout_f, authenticate, login as login_f
from django.http import JsonResponse
from querystring_parser import parser
from celery.result import AsyncResult
from datetime import datetime
from django.db.models import Count, Sum
from django.contrib.auth.models import User
import pprint
import redis
import json




# Create your views here.
from gtt.models import Data, Resource, Template, Task, TradeInfo, Country, Statistic, DirectionType, AnalyzedTradeInfo


def get_val(request):
    country = Country.country.filter(id__exact=request.POST['country'])
    if country:
        data = AnalyzedTradeInfo.info.filter(country__exact=country[0])
        if request.POST['partner']:
            partner = Country.country.filter(id__exact=request.POST['partner'])
            if partner:
                data = data.filter(partner__exact=partner[0])
        if request.POST['dir_type']:
            dir_type = DirectionType.objects.filter(id__exact=request.POST['dir_type'])
            if dir_type:
                data = data.filter(direction_type__exact=dir_type[0])
        if request.POST['year'] != "0":
            data = data.filter(year__exact=request.POST['year'])
        result = []
        if data:
            for d in data:
                result.append({
                    'id': d.id,
                    'country': {
                        'id': d.country.id,
                        'rus': d.country.rus
                    },
                    'partner': {
                        'id': d.partner.id,
                        'rus': d.partner.rus
                    },
                    'dir_type': {
                        'id': d.direction_type.id,
                        'rus': d.direction_type.rus
                    },
                    'year': d.year,
                    'value': d.value
                })
            graph = data.values('year').annotate(Sum('value'))
            graph_result = []
            if graph:
                for g in graph:
                    graph_result.append({
                        'year': g['year'],
                        'year__sum': g['value__sum']
                    })
            return JsonResponse({'data': result, 'graph': graph_result}, safe=False)
        else:
            return JsonResponse(False, safe=False)
    else:
        return JsonResponse(False, safe=False)


def get_koef(request):
    country = Country.country.filter(id__exact=request.POST['country'])
    if country:
        stats = Statistic.statistic.filter(country__exact=country[0]).filter(year__exact=request.POST['year']).\
            order_by('-index')
        result = []
        if stats:
            for stat in stats:
                result.append({
                    'id': stat.id,
                    'country': {
                        'id': stat.country.id,
                        'rus': stat.country.rus
                    },
                    'partner': {
                        'id': stat.partner.id,
                        'rus': stat.partner.rus
                    },
                    'index': stat.index
                })
        else:
            result = False
        return JsonResponse(result, safe=False)
    else:
        return JsonResponse(False, safe=False)


def temporary(request):
    countries_eng = "Afghanistan|Angola|Albania|United Arab Emirates|Argentina|Armenia|Antarctica|Kerguelen|Australia|Austria|Azerbaijan|Burundi|Belgium|Benin|Burkina Faso|Bangladesh|Bulgaria|Bahamas|Bosnia and Herzegovina|Belarus|Belize|Bolivia, Plurinational State of|Brazil|Brunei Darussalam|Bhutan|Botswana|Central African Republic|Canada|Switzerland|Chile|China |Cote d'Ivoire|Cameroon|Congo, Democratic Republic of the|Congo|Colombia|Costa Rica|Cuba|Northern Cyprus|Cyprus|Czech Republic|Germany |Djibouti|Denmark|Dominican Republic|Algeria|Ecuador|Egypt|Eritrea|Spain|Estonia|Ethiopia|Finland|Fiji|Falkland Islands (Malvinas)|Guyana|Gabon|United Kingdom |Georgia|Ghana|Guinea|Gambia|Guinea-Bissau|Equatorial Guinea|Greece|Greenland|Guatemala|Guyana|Honduras|Croatia|Haiti|Hungary|Indonesia|India|Ireland|Iran, Islamic Republic of|Iraq|Iceland|Israel|Italy|Jamaica|Jordan|Japan|Kazakhstan|Kenya|Kyrgyzstan|Cambodia|Korea, Republic of|Kosovo|Kuwait|Laos|Lebanon|Liberia|Libya, State of|Sri Lanka|Lesotho|Lithuania|Luxembourg|Latvia|Morocco|Moldova, Republic of|Madagascar|Mexico|Macedonia, The Former Yugoslav Republic of|Mali|Myanmar|Montenegro|Mongolia|Mozambique|Mauritania|Malawi|Malaysia|Namibia|New Caledonia|Niger|Nigeria|Nicaragua|Netherlands|Norway|Nepal|New Zealand|Oman|Pakistan|Panama|Peru|Philippines|Papua New Guinea|Poland|Puerto Rico|Korea, Democratic People's Republic of|Portugal|Paraguay|Palestine, State of|Qatar|Romania|Russian Federation|Rwanda|Western Sahara|Saudi Arabia|Sudan|South Sudan|Senegal|Solomon Islands|Sierra Leone|Salvador|Somaliland|Somalia|Serbia|Suriname|Slovakia|Slovenia|Sweden|Swaziland|Syria Arab Republic|Chad|Togo|Thailand|Tajikistan|Turkmenistan|Timor-Leste|Trinidad and Tobago|Tunisia|Turkey|Taiwan|Tanzania, United Republic of|Uganda|Ukraine|Uruguay|United States of America|Uzbekistan|Venezuela, Bolivarian Republic of|Viet Nam|Vanuatu|Yemen|South Africa|Zambia|Zimbabwe|France"
    countries_rus = "Афганистан|Ангола|Албания|Объединенные Арабские Эмираты|Аргентина|Армения|Антарктида|Кергелен|Австралия|Австрия|Азербайджан|Бурунди|Бельгия|Бенин|Буркина-Фасо|Бангладеш|Болгария|Багамские острова|Босния и Герцеговина|Беларусь|Белиз|Боливия|Бразилия|Бруней|Бутан|Ботсвана|Центральноафриканская республика|Канада|Швейцария|Чили|Китай|Кот-Д'ивуар|Камерун|Демократическая республика Конго|Конго|Колумбия|Коста-Рика|Куба|Турецкий Кипр|Кипр|Чехия|Германия|Джибути|Дания|Доминиканская Республика|Алжир|Эквадор|Египет|Эритрея|Испания|Эстония|Эфиопия|Финляндия|Фиджи|Фолклендские острова|Гвиана|Габон|Великобритания|Грузия|Гана|Гвинея|Гамбия|Гвинея-Бисау|Экваториальная Гвинея|Греция|Гренландия|Гватемала|Гайана|Гондурас|Хорватия|Гаити|Венгрия|Индонезия|Индия|Ирландия|Иран|Ирак|Исландия|Израиль|Италия|Ямайка|Иордания|Япония|Казахстан|Кения|Киргизия|Камбоджа|Республика Корея|Косово|Кувейт|Лаос|Ливан|Либерия|Ливия|Шри-Ланка|Лесото|Литва|Люксембург|Латвия|Марокко|Молдова|Мадагаскар|Мексика|Македония|Мали|Мьянма|Черногория|Монголия|Мозамбик|Мавритания|Малави|Малайзия|Намибия|Новая Каледония|Нигер|Нигерия|Никарагуа|Нидерланды|Норвегия|Непал|Новая Зеландия|Оман|Пакистан|Панама|Перу|Филиппины|Папуа - Новая Гвинея|Польша|Пуэрто-Рико|Корейская Народно-Демократическая Республика|Португалия|Парагвай|Палестина|Катар|Румыния|Россия|Руанда|Западная Сахара|Саудовская Аравия|Судан|Южный Судан|Сенегал|Соломоновы острова|Сьерра-Леоне|Сальвадор|Сомалиленд|Сомали|Сербия|Суринам|Словакия|Словения|Швеция|Свазиленд|Сирия|Чад|Того|Таиланд|Таджикистан|Туркмения|Восточный Тимор|Тринидад и Тобаго|Тунис|Турция|Тайвань|Танзания|Уганда|Украина|Уругвай|США|Узбекистан|Венесуэла|Вьетнам|Вануату|Йемен|ЮАР|Замбия|Зимбабве|Франция"
    countries_eng_list = countries_eng.split("|")
    countries_rus_list = countries_rus.split("|")
    for country_n in range(len(countries_eng_list)):
        c = Country.country.create(id=country_n+1, code=countries_eng_list[country_n], rus=countries_rus_list[country_n])
        c.save()
    return JsonResponse(True, safe=False)


def home(request):
    # r = redis.StrictRedis(host='localhost', port=6379, db=0)
    # keys = r.keys()
    # for key in keys:
    #     r.delete(key)

    countries = Country.country.order_by('rus')
    years = Statistic.statistic.order_by('-year').values('year').distinct()
    dir_types = DirectionType.objects.all()
    return render(request, 'gtt/home.html', {'countries': countries,
                                             'years': years,
                                             'dir_types': dir_types})


def process_status_by_resource(resource):
    tasks = Task.task.filter(resource__exact=resource).order_by('-date_start')[:10]
    if tasks:
        return processes_status(tasks, True)
    else:
        return []


def processes_status(tasks, return_all_task=False):
    tasks_status = []
    for task in tasks:
        if task.date_end:
            status = 100
        else:
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


def parsing(request):
    resource = Resource.resource.filter(id__exact=request.POST['id'])
    if resource:
        data = Data()
        data.grab_the_site(resource[0])
        return JsonResponse(0, safe=False)
    else:
        return JsonResponse(1, safe=False)


def analyze(request):
    resource = Resource.resource.filter(id__exact=request.POST['id'])
    if resource:
        data = Data()
        data.analyze(resource[0])
        return JsonResponse(0, safe=False)
    else:
        return JsonResponse(1, safe=False)


def aggregation(request):
    resource = Resource.resource.filter(id__exact=request.POST['id'])
    if resource:
        data = Data()
        data.aggregation(resource[0])
        return JsonResponse(0, safe=False)
    else:
        return JsonResponse(1, safe=False)


def koef_eval(request):
    resource = Resource.resource.filter(id__exact=request.POST['id'])
    if resource:
        data = Data()
        data.koef_eval(resource[0])
        return JsonResponse(0, safe=False)
    else:
        return JsonResponse(1, safe=False)


def admin(request):
    if request.user.is_authenticated():
        username = request.user.get_full_name()
        registered_date = request.user.date_joined.strftime("%d.%m.%Y %H:%M")
        parsings = Task.task.filter(name__icontains="Парсинг").count()
        analyzes = Task.task.filter(name__icontains="Анализ").count()
        aggrations = Task.task.filter(name__icontains="Объединение").count()
        ke = Task.task.filter(name__icontains="Пересчет").count()
        vals_by_year = TradeInfo.info.values('year').annotate(value=Count('value'))
        tasks = Task.task.filter(date_end__exact=None).order_by('-date_start')[:5]
        return render(request, 'gtt/admin/dashboard.html', {'superuser': request.user.is_superuser,
                                                            'username': username, 'registered_date': registered_date,
                                                            'pars': parsings, 'analyzes': analyzes,
                                                            'aggrs': aggrations, 'ke': ke,
                                                            'vals_by_year': vals_by_year, 'tasks': tasks})
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
        return render(request, 'gtt/admin/resources.html', {'superuser': request.user.is_superuser,
                                                            'username': username, 'registered_date': registered_date,
                                                            'resources': res})
    else:
        return HttpResponse(status=404)


def administrators(request):
    if request.user.is_authenticated() and request.user.is_superuser:
        username = request.user.get_full_name()
        registered_date = request.user.date_joined.strftime("%d.%m.%Y %H:%M")
        us = User.objects.all()
        return render(request, 'gtt/admin/administrators.html', {'superuser': request.user.is_superuser,
                                                                 'username': username,
                                                                 'registered_date': registered_date,
                                                                 'users': us})
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


def add_user(request):
    if request.user.is_authenticated() and request.user.is_superuser:
        uss = User.objects.filter(username__exact=request.POST['username'])
        if uss:
            return JsonResponse(False, safe=False)
        if request.POST.get('is_superuser'):
            us = User.objects.create_superuser(request.POST['username'], request.POST['email'], request.POST['password'])
        else:
            us = User.objects.create_user(request.POST['username'], request.POST['email'], request.POST['password'])

        us.first_name = request.POST['first_name']
        us.last_name = request.POST['last_name']
        us.save()
        return JsonResponse({'id': us.id, 'name': us.get_full_name()}, safe=False)
    else:
        return HttpResponse(status=404)


def edit_user(request):
    if request.user.is_authenticated() and request.user.is_superuser:
        try:
            us = User.objects.get(id=request.POST['id'])
            uss = User.objects.filter(username__exact=request.POST['username'])
            if uss and us.username != uss[0].username:
                return JsonResponse(2, safe=False)
            us.first_name = request.POST['first_name']
            us.last_name = request.POST['last_name']
            if request.POST['password']:
                us.set_password(request.POST['password'])
            us.email = request.POST['email']
            if request.POST.get('is_superuser'):
                us.is_superuser = 1
            else:
                us.is_superuser = 0
            us.save()
        except Resource.DoesNotExist:
            return JsonResponse(False, safe=False)
        else:
            return JsonResponse(us.get_full_name(), safe=False)
    else:
        return HttpResponse(status=404)


def get_user(request):
    if request.user.is_authenticated() and request.user.is_superuser:
        try:
            us = User.objects.get(id=request.POST['id'])
        except User.DoesNotExist:
            return JsonResponse(False, safe=False)
        else:
            result = {"first_name": us.first_name,
                      "last_name": us.last_name,
                      "email": us.email,
                      "username": us.username,
                      "is_superuser": us.is_superuser}
            return JsonResponse(result, safe=False)
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


def delete_user(request):
    if request.user.is_authenticated() and request.user.is_superuser:
        try:
            us = User.objects.get(id=request.POST['id'])
            us.delete()
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
        return render(request, 'gtt/admin/operations.html', {'superuser': request.user.is_superuser,
                                                             'username': username, 'registered_date': registered_date,
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
