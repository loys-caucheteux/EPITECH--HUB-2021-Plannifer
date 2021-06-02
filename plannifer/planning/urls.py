from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings

app_name = 'planning'

urlpatterns = [
    path('', views.index, name='index'),
    path('account/register', views.register, name='register'),
    path('calendar/<int:home_id>', views.calendar_view, name='calendar'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('homes/<home_id>', views.home_handler, name='home_handler'),
    path('homes/<home_id>/tasks/', views.task_plan, name='task_plan'),
    path('forms/add_home', views.add_home, name='add_home'),
    path('users/<int:uid>', views.profile_view, name='profile_view'),
    path('homes/<int:home_id>/users', views.user_view, name='user_view'),
    path('denounce/<int:task_id>', views.denonce_task, name='del_task'),
    path('add_user/<int:home_id>', views.add_user, name='add_user'),
    path('task/<int:task_id>', views.edit_task, name='edit_task'),
    path('task/<int:task_id>/cancel', views.cancel_denonce, name='cancel'),
    path('purchase/', views.checkout, name='purchase'),
    path('support/', views.support, name='support'),
    path('thanks/', views.thanks, name='thanks'),
    path('1Xk36LppqkSp6Ev3oD/', views.secret, name='1Xk36LppqkSp6Ev3oD'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

