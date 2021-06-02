from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse
from django.template import loader
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from .forms import *
from django.contrib.auth.decorators import login_required
from datetime import datetime, date, timedelta
from django.views import generic
from django.utils.safestring import mark_safe
import calendar
import stripe
from .models import *
from .utils import *
import os

ADRESS = 'https://plannifer.herokuapp.com/'

# I hope that your linter brought you here and now you are disappointed
if os.environ.get('ENV') == 'PRODUCTION':
    stripe.api_key = os.environ.get('STRIPE_KEY')
else:
    stripe.api_key = 'sk_test_51IuLgyGMLF5BaxFNQP8nMiAN15Wo1apRemLohymjmK60cKCeKKGfh6rXXE76bdGzdClncdqQF4zmQgKjwKR3EvRx00bLEA0q3Q'

def index(request):
    if request.user.is_authenticated:
        return redirect("planning:dashboard")
    return render(request, 'planning/index.html')

@transaction.atomic
def register(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = RegisterUserForm(request.POST, error_class=ParagraphErrorList)
            if form.is_valid():
                email = form.cleaned_data['mail']
                pwd = form.cleaned_data['pwd']
                name = form.cleaned_data['name']
                surname = form.cleaned_data['surname']
                pseudo = form.cleaned_data['pseudo']
                user = User.objects.filter(username=pseudo)
                user2 = User.objects.filter(email=email)
                if not user.exists():
                    if user2.exists():
                        context = {
                        'form' : RegisterUserForm(),
                        'used': 'email'
                        }
                        return render(request, 'registration/register.html', context)
                    else:
                        User.objects.create_user(pseudo, email=email,
                        password=pwd, first_name=name,
                        last_name=surname
                        )
                        luser = authenticate(request, username=pseudo, password=pwd)
                        profile = Profile(user=luser, stars=0)
                        profile.save()
                        login(request, luser)
                        return redirect("planning:index")
                else:
                    context = {
                        'form' : RegisterUserForm(),
                        'used': 'pseudo'
                        }
                    return render(request, 'registration/register.html', context)
            else:
                context['errors'] = form.errors.items()
        else:
            a = 0
    else:
        return redirect("planning:index")
    context = {'form' : RegisterUserForm()}
    return render(request, 'registration/register.html', context)

@login_required
def profile_view(request, uid):
    if request.user.is_authenticated:
        profile = get_object_or_404(Profile, user_id=uid)
        homes = profile.homes.all()
        common_homes = []
        for home in homes:
            if request.user.profile in home.profile_set.all():
                common_homes.append(home)
        return render(request, 'planning/profile.html', {'homes': mark_safe(ProfileHomes(common_homes, profile).format_homes()), 'profile': profile})

@login_required
def dashboard(request):
    profile = Profile.objects.get(user_id=request.user.pk)
    homes_menu = HomeList(profile=profile)
    context = {'homeform' : AddHomeForm(), 'homes' : mark_safe(homes_menu.home_menu(profile=profile))}
    return render(request, 'user/dashboard.html', context)

@login_required
def task_plan(request, home_id):
    context = {}
    try:
        hid = int(home_id)
    except ValueError:
        return redirect("planning:index")
    home = get_object_or_404(Home, pk=hid)
    profiles = home.profile_set.all()
    for profile in profiles:
        if (profile.user.pk == request.user.pk):
            if request.method == 'POST':
                form = CreateTaskForm(request.POST, home=hid, error_class=ParagraphErrorList)
                if form.is_valid():
                    hometask = HomeTask.objects.get(pk=form.cleaned_data['home_task'])
                    newdoer = Profile.objects.get(user_id=form.cleaned_data['doer'])
                    if form.cleaned_data['spent'] != None:
                        newtask = Task(
                            title=form.cleaned_data['title'],
                            description=form.cleaned_data['description'],
                            creator=request.user.profile,
                            doer=newdoer,
                            home=home,
                            home_task=hometask,
                            difficulty=hometask.difficulty,
                            start_time=form.cleaned_data['start_time'],
                            end_time=form.cleaned_data['end_time'],
                            spent=Spent.objects.create(home=home, user=newdoer, title=form.cleaned_data['title'], amount=form.cleaned_data['spent'])
                        )
                    else:
                        newtask = Task(
                            title=form.cleaned_data['title'],
                            description=form.cleaned_data['description'],
                            creator=request.user.profile,
                            doer=newdoer,
                            home=home,
                            home_task=hometask,
                            difficulty=hometask.difficulty,
                            start_time=form.cleaned_data['start_time'],
                            end_time=form.cleaned_data['end_time']
                        )
                    newtask.save()
                    newdoer.stars += newtask.difficulty
                    newdoer.save()
            context['taskform'] = CreateTaskForm(home=hid)
            context['task_plan'] = mark_safe(TaskPlan(home=home).task_plan())
            context['home'] = home
            return render(request, 'planning/task_plan.html', context)
    return Http404()

@login_required
def home_handler(request, home_id):
    context = {}
    try:
        hid = int(home_id)
    except ValueError:
        return redirect("planning:index")
    home = get_object_or_404(Home, pk=hid)
    if (home.creator.pk != request.user.pk):
        raise Http404("What is this all about ?")
    if request.method == 'POST':
        if request.GET['form'] == 'user':
            form = AddUserForm(request.POST, error_class=ParagraphErrorList)
            if form.is_valid():
                username = form.cleaned_data['username']
                user = User.objects.filter(username=username)
                if user.exists():
                    user.first().profile.homes.add(home)
                else:
                    context['bad'] = 'user'
            else:
                context['errors'] = form.errors.items()
        elif request.GET['form'] == 'task':
            form = AddTaskForm(request.POST, error_class=ParagraphErrorList)
        if form.is_valid():
            name = form.cleaned_data['name']
            diff = form.cleaned_data['difficulty']
            new_task = HomeTask(home=home,
            creator=request.user,
            name=name,
            difficulty=diff)
            new_task.save()
        else:
            context['errors'] = form.errors.items()
    context['home'] = home
    context['adduserform'] = AddUserForm()
    context['addtaskform'] = AddTaskForm()
    context['users'] = mark_safe(UserList(home=home).user_menu())
    context['tasks'] = mark_safe(TasksList(home=home).task_menu())
    return render(request, 'user/home_handler.html', context)

@login_required
def denonce_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    profiles = task.home.profile_set.all()
    prof = profiles.filter(user__id=request.user.pk)
    if len(prof) > 0 and task.denonceur == None:
        task.denonceur = prof.first()
        task.doer.stars -= task.difficulty
        task.doer.save()
        task.save()
        return redirect(f"{ADRESS}{request.GET.get('prev', '')}")
    else: return redirect("planning:index")

@login_required
def cancel_denonce(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if task.denonceur != None:
        if request.user.pk == task.denonceur.user.pk or request.user.pk == task.home.creator.pk:
            task.denonceur = None
            task.doer.stars += task.difficulty
            task.doer.save()
            task.save()
            return redirect(f"{ADRESS}{request.GET.get('prev', '')}")
        else:
            return redirect('planning:index')
    else: return redirect('planning:index')

@login_required
def add_user(request, home_id):
    context = {}
    if request.method == 'POST':
        form = AddUserForm(request.POST, error_class=ParagraphErrorList)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user = User.objects.get(username=username)
                pro = Profile.objects.get(user_id=user.id)
                home = Home.objects.get(id=home_id)
                pro.homes.add(home)
                pro.save()
                return(redirect('planning:user_view', home_id=home_id))
            except ObjectDoesNotExist: 
                return redirect(f'{ADRESS}homes/{home_id}/users?u=n')
        else: return redirect(f'{ADRESS}homes/{home_id}/users?u=n')
    else: return redirect('planning:user_view')

@login_required
def add_home(request):
    context = {}
    f = True
    if request.method == 'POST':
        form = AddHomeForm(request.POST, error_class=ParagraphErrorList)
        if form.is_valid():
            name = form.cleaned_data['name']
            pro = Profile.objects.get(user=request.user)
            try:
                home = pro.homes.get(name=name)
            except ObjectDoesNotExist:
                if (request.user.profile.is_premium):
                    new_home = Home(creator=request.user, name=name)
                else:
                    new_home = Home(creator_id=1, name=name)
                new_home.save()
                pro.homes.add(new_home)
                pro.save()
                create_home_foyer(new_home)
                return redirect("planning:dashboard")
            return redirect(f'{ADRESS}dashboard?used=name')
        else:
            context['errors'] = form.errors.items()
    elif True:
        context['homeform'] = AddHomeForm()
        return render(request, 'user/dashboard.html', context)
    else:
        return redirect("planning:index", used='name')

@login_required
def user_view(request, home_id):
    context = {}
    home = get_object_or_404(Home, pk=home_id)
    return render(request, 'user/home_users.html', context={'home': home,
        'users': mark_safe(UserView(home, request.user).tableUser()),
        'userform': AddUserForm()})
        
@login_required
def edit_task(request, task_id):
    context = {}
    task = get_object_or_404(Task, pk=task_id)
    if request.user.pk == task.doer.user.pk or request.user.pk == task.creator.user.pk or request.user.pk == task.home.creator.pk:
        if request.GET.get('d', None) == 'y':
            task.doer.stars -= task.difficulty
            task.doer.save()
            task.delete()
            return redirect('planning:user_view', task.home.pk)
        elif request.method == 'POST':
            form = EditTaskForm(request.POST, task=task, error_class=ParagraphErrorList)
            if form.is_valid():
                try:
                    spenty = form.cleaned_data['spent']
                except KeyError:
                    spenty = None
                task.title = form.cleaned_data['title']
                task.description = form.cleaned_data['description']
                task.start_time =  form.cleaned_data['start_time']
                task.end_time = form.cleaned_data['end_time']
                if spenty != None:
                    task.spent = spenty
                task.save()
                return redirect('planning:user_view', task.home.pk)
            else:
                context['errors'] = form.errors.items()
        context['taskform'] = EditTaskForm(task=task)
        context['home'] = task.home
        context['task'] = task
        return render(request, 'planning/task_edit.html', context)
    else: return redirect('planning:index')

@login_required
def calendar_view(request, home_id):
    context = {}
    d = get_date(request.GET.get('month', None))
    cal = Calendar(d.year, d.month, home_id)
    html_cal = cal.formatmonth(withyear=True)
    context['calendar'] = mark_safe(html_cal)
    context['dateform'] = SelectMonthForm()
    context['prev_month'] = prev_month(d)
    context['next_month'] = next_month(d)
    context['home'] = Home.objects.get(id=home_id)
    return render(request, 'planning/calendar.html', context)

def secret(request):
    intent = stripe.PaymentIntent.create(
        amount=200,
        currency='eur',
        metadata={'integration_check': 'accept_a_payment'},
    )
    return JsonResponse({"client_secret": intent.client_secret})

@login_required
def checkout(request):
    return render(request, 'registration/purchase.html')

@login_required
def support(request):
    return render(request, 'registration/sell.html')

@login_required
def thanks(request):
    request.user.profile.is_premium = True
    request.user.profile.save()
    return render(request, 'registration/thanks.html')

def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()

def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month