from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^article/(?P<article_id>[0-9]+)/$', views.article, name='article'),
    url(r'^data[/]$', views.data, name='data'),
    url(r'^admin[/]$', views.admin, name='admin'),
    url(r'^login[/]$', views.login, name='login'),
    url(r'^logout[/]$', views.logout, name='logout'),
    url(r'^admin/resources[/]$', views.resources, name='resources'),
    url(r'^admin/resources/add_resource[/]$', views.add_resource, name='add_resource'),
    url(r'^admin/resources/get_resource[/]$', views.get_resource, name='get_resource'),
    url(r'^admin/resources/edit_resource[/]$', views.edit_resource, name='edit_resource'),
    url(r'^admin/resources/delete_resource[/]$', views.delete_resource, name='delete_resource'),
]
