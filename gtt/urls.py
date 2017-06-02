from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^admin[/]$', views.admin, name='admin'),
    url(r'^login[/]$', views.login, name='login'),
    url(r'^logout[/]$', views.logout, name='logout'),
    url(r'^admin/resources[/]$', views.resources, name='resources'),
    url(r'^admin/resources/add_resource[/]$', views.add_resource, name='add_resource'),
    url(r'^admin/resources/get_resource[/]$', views.get_resource, name='get_resource'),
    url(r'^admin/resources/edit_resource[/]$', views.edit_resource, name='edit_resource'),
    url(r'^admin/resources/delete_resource[/]$', views.delete_resource, name='delete_resource'),
    url(r'^admin/operations[/]$', views.operations, name='operations'),
    url(r'^admin/operations/get_task_statuses[/]$', views.get_tasks_statuses, name='get_tasks_statuses'),
    url(r'^admin/operations/tasks_statuses_by_resource[/]$', views.tasks_statuses_by_resource, name='tasks_statuses_by_resource'),
    url(r'^admin/operations/parsing[/]$', views.parsing, name='parsing'),
]
