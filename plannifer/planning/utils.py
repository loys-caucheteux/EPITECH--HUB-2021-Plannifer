from datetime import datetime, timedelta
from calendar import HTMLCalendar
from .models import Task, Profile, Home, HomeTask

ADRESS = 'https://plannifer.herokuapp.com/'
months_list = ["BlaBla", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sept", "Oct", "Nov", "Dec"]

class Calendar(HTMLCalendar):
	def __init__(self, year=None, month=None, home=None):
		self.year = year
		self.month = month
		self.home = home
		super(Calendar, self).__init__()

	# formats a day as a td
	# filter events by day
	def formatday(self, day, events):
		events_per_day = events.filter(start_time__day=day)
		d = ''
		for event in events_per_day:
			d += f'<li>{event.home_task.name}<br/>{event.doer.user.username}<br/>{event.start_time.strftime("%H:%M")}</li>'


		if day != 0:
			return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
		return '<td></td>'

	# formats a week as a tr 
	def formatweek(self, theweek, events):
		week = ''
		for d, weekday in theweek:
			week += self.formatday(d, events)
		return f'<tr> {week} </tr>'

	# formats a month as a table
	# filter events by year and month
	def formatmonth(self, withyear=True):
		events = Task.objects.all()
		events = events.filter(home_id=self.home, start_time__month=self.month)
		cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
		cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
		cal += f'{self.formatweekheader()}\n'
		for week in self.monthdays2calendar(self.year, self.month):
			cal += f'{self.formatweek(week, events)}\n'
		return cal


class WeekPlanning(HTMLCalendar):
	def __init__(self, year=None, month=None, day=None, home=None):
		self.year = year
		self.month = month
		self.home = home
		self.day = day
		super(WeekPlanning, self).__init__()

	# formats a day as a td
	# filter events by day
	def format_hours(self, hour_int, events):
		hour = ''
		events_per_hour = events.filter(start_time__hour=hour_int)
		if events_per_hour.exists():
			for event in events_per_hour:
				hour += f'<li>{event.home_task.name}<br/><a href="{ADRESS}users/{event.doer.user.id}">{event.doer.user.username}</a><br/>{event.start_time.strftime("%H:%M")}</li>'
		else:
			return '<div class="row><br/></div>\n'
		return f'<div class="row"><ul>{hour}</ul></div>\n'

	def formatday(self, day, events):
		events_per_day = events.filter(start_time__day=day)
		d = ''
		for i in range(1, 24):
			d += self.format_hours(i, events_per_day)
		return f'<div class="col">\n {d}\n </div>'

	def formatweek(self, theweek, events):
		week = ''
		for d, weekday in theweek:
			week += self.formatday(d, events)
		return f'<div class="container"> \n{week} \n</div>'

	def format_plan(self):
		events = Task.objects.all()
		events = events.filter(home_id=self.home)
		cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
		cal +=  f'{self.formatweekheader()}\n'
		cal += f'</table>\n'
		for week in self.monthdays2calendar(self.year, self.month):
			for day in week:
				if self.day in day:
					cal += f'{self.formatweek(week, events)}\n'
		return cal


class HomeList():
	def __init__(self, profile=None):
		self.profile = profile
	
	#formate 5 colonnes qui peuvent contenir chacune 1 case /bouton maison
	def home_menu(self, profile):
		i = 0
		menu = f'<div class="row mt-4">\n'
		homes = profile.homes.all()
		for home in homes:
			menu += self.home_case(home)
			i += 1
			if (i == 3):
				menu += f'<div class="w-100"></div>'
				i = 0
		menu += f'</div>'
		return menu
	def home_case(self, home):
		case = f'<div class="col mt-4 text-center">\n'
		case += f'<h2 class="border">{home.name}</h2>\n'
		if (home.creator.id == self.profile.user.id):
			case += f'<a class="row btn col-md-6 btn-lg btn-danger mt-1" href="{ADRESS}homes/{home.pk}"><span class="col-md-10">Admin Panel</span><span class="col-md-2" data-feather="chevrons-up"></span></a><br/>\n'
		case += f'<a class="row btn btn-lg col-md-6 btn-primary mt-1" href="{ADRESS}calendar/{home.pk}"><span class="col-md-10">Calendar</span><i style="align:center" class="col-md-2" data-feather="calendar"></i></a><br/>\n'
		case += f'<a class="row btn btn-lg col-md-6 btn-success mt-1" href="{ADRESS}homes/{home.pk}/tasks"><span class="col-md-10">View & Add Tasks</span><i class="col-md-2" data-feather="check"></i></a><br/>\n'
		case += f'<a class="row btn  btn-lg col-md-6 btn-primary mt-1" href="{ADRESS}homes/{home.pk}/users"><span class="col-md-10">Users</span><i class="col-md-2" data-feather="users"></i></a><br/>\n'
		case += f'</div></div>\n'
		return case


class UserList():
	def __init__(self, home):
		self.home = home
	#formate 5 colonnes qui peuvent contenir chacune 1 case /bouton maison
	def user_menu(self):
		menu = f'<table class="table mt-2 table-striped">\n'
		menu += f'<tr><th>Pseudo</th><th>Name</th></tr>\n'
		users = self.home.profile_set.all()
		for user in users:
			menu += self.user_case(user)
		menu += f'</table>'
		return menu
	def user_case(self, user):
		case = f'<tr>\n'
		case += f'<td>{user.user.username}</td>\n'
		case += f'<td>{user.user.first_name} {user.user.last_name}</td>\n'
		case += f'</tr>\n'
		return case


class TasksList():
	def __init__(self, home):
		self.home = home
		self.date = datetime.now()
	#formate 5 colonnes qui peuvent contenir chacune 1 case /bouton maison
	def format_difficulty(self, difficulty):
		stars = '<td style="color:rgb(207, 204, 8);"><i data-feather="star"></i>'
		for i in range(difficulty - 1):
			stars += '<i data-feather="star"></i>'
		stars += '</td>'

		return stars
	def task_menu(self):
		menu = f'<table class="table mt-2 table-striped">\n'
		menu += f'<tr><th>Task name</th><th>Stars</th></tr>\n'
		tasks = self.home.hometask_set.all()
		i = 0
		for task in tasks:
			menu += self.task_case(task, i)
			i += 1
		menu += f'</table>\n'
		return menu
	def task_case(self, task, i):
		case = f'<tr>\n'
		case += f'<td>{task.name}</td>'
		case += f'{self.format_difficulty(task.difficulty)}'
		case += f'</tr>\n'
		return case


class ProfileHomes():
	def __init__(self, homes, user):
		self.homes = homes
		self.user = user

	def format_difficulty(self, difficulty):
		stars = '<span class="col-md-5" style="color:rgb(207, 204, 8);"><span data-feather="star"></span>'
		for i in range(difficulty - 1):
			stars += '<span data-feather="star"></span>'
		stars += '</span>'
		return stars

	def format_home(self, home):
		tasks = home.task_set.all().filter(doer=self.user)
		table = f'<table class="table table-striped table-hover col-md-12 mb-3">\n'
		table += f'<thead><tr><th>Shore</th><th>Complexity</th><th>Date, time</th><th>Cost</th></tr></thead>\n'
		i = 0
		for task in tasks:
			table += f'''<td>{task.home_task.name}</td>\n
			<td>{self.format_difficulty(task.home_task.difficulty)}</td>\n
			<td>{task.start_time.strftime("%d-%m, %H:%M")}</td>\n'''
			if task.spent != None:
				table += f'<td>{task.spent.amount} $</td>\n'
			else: table += f'<td></td>\n'
			if task.denonceur == None:
				table += f'<td><a class="mt-1 mb-1 btn btn-sm btn-outline-danger" href="{ADRESS}denounce/{task.id}?prev=users/{self.user.user.pk}"><span class="align-middle">Denounce<span data-feather="x"></span></span></a></td>\n'
			else:
				table += f'<td><span style="color:rgb(207, 100, 0);">Denounced by {task.denonceur.user.first_name}</span></td>\n'
			table += '</tr>\n'
			i += 1
		table += '</table>\n'
		return table
			
	def format_homes(self):
		homes = '<div class="row">\n'
		i = 0
		for home in self.homes:
			if i % 2 == 0:
				homes += f'<div class="row btn-user rounded-3">'
			else:
				homes += f'<div class="row btn-user2 rounded-3">'
			homes += f'<h3 class="col-md-11"><center><a href="{ADRESS}homes/{home.pk}/tasks">{home.name}</a></center></h3>'
			homes += f'''<button class="btn-sm mt-2 mb-2 btn btn-primary col-md-1" type="button" data-bs-toggle="collapse" data-bs-target="#{home.creator.username}{home.pk}" aria-expanded="false" aria-label="{home.creator.username} {home.pk}">
			<i data-feather="arrow-down"></i></button></div>'''
			homes += f'<div class="collapse" id="{home.creator.username}{home.pk}">\n'
			homes += self.format_home(home)
			homes += '</div>'
			i += 1
		homes += '</div>'
		return homes


class UserView():
	def __init__(self, home, user):
		self.home = home
		self.user = user
		self.date = datetime.today()

	def format_difficulty(self, difficulty):
		stars = '<span class="d-inline" style="color:rgb(207, 204, 8);">\n<span data-feather="star"></span>\n'
		for i in range(difficulty - 1):
			stars += '<span data-feather="star"></span>\n'
		stars += '</span>\n'
		return stars

	def format_user(self, user):
		table = f'<table class="table table-striped table-hover col-md-12 mb-3 mt-3">\n'
		table += f'<thead><tr><th>Shore</th><th>Complexity</th><th>Date, time</th><th>Cost</th></tr></thead>\n'
		i = 0
		for task in user.doer.all().filter(home=self.home).filter(start_time__month=self.date.month).order_by('start_time'):
			table += f'''<tr><td>{task.home_task.name}</td>\n
			<td>{self.format_difficulty(task.home_task.difficulty)}</td>\n
			<td>{task.start_time.strftime("%d")} {months_list[task.start_time.month]} {task.start_time.strftime(", %H:%M")}</td>'''
			if task.spent != None:
				table += f'<td>{task.spent.amount} €</td>\n'
			else: table += f'<td></td>\n'
			if task.denonceur == None:
				table += f'<td><a class="mt-1 mb-1 btn btn-sm btn-outline-danger" href="{ADRESS}denounce/{task.id}?prev=homes/{self.home.pk}/users"><span class="align-middle">Denounce<span data-feather="x"></span></span></a></td>\n'
			else:
				table += f'<td><span class="align-middle" style="color:rgb(207, 100, 0);">Denounced by {task.denonceur.user.first_name}</span>'
				if task.denonceur.user.pk == self.user.pk:
					table += f'<span class="align-bottom" style="font-size:smaller">  <a href="{ADRESS}task/{task.pk}/cancel?prev=homes/{self.home.pk}/users">Cancel</a></span>\n'
				table += '</td>'
			if self.user.pk == task.home.creator.pk or self.user.pk == task.creator.user.pk:
				table += f'<td><a href="{ADRESS}task/{task.pk}"><i data-feather="edit-2"></i>Modifier</a></td>'
			table += '</tr>\n'
			i += 1
		table += '</table>\n'
		return table
	
	def tableUser(self):
		table = f'<div class="row">\n'
		i = 0
		for user in self.home.profile_set.all():
			if (i % 2):
				table += f'<div class="row btn-user2 rounded-3">'
			else :
				table += f'<div class="row btn-user rounded-3">'
			table += f'<h3 class="col-md-11"><center><a href="{ADRESS}users/{user.user.pk}">{user.user.first_name} {user.user.last_name}</a></center></h3>\n'
			table += f'<button class="btn btn-sm mt-2 mb-2 col-md-1 btn-primary" type="button" data-bs-toggle="collapse" data-bs-target="#{user.user.username}" aria-controls="{user.user.username}" aria-expanded="false" aria-label="{user.user.first_name}"><i data-feather="arrow-down"></i></button></div>'
			table += f'<div class="collapse" id="{user.user.username}">\n'
			table += self.format_user(user)
			table += f'</div>\n'
			i += 1
		return table


class TaskPlan():
	def __init__(self, home):
		self.home = home
		self.date = datetime.today()
	#formate 5 colonnes qui peuvent contenir chacune 1 case/bouton maison
	def task_plan(self):
		menu = f'<div class="container row">\n'
		tasks = self.home.hometask_set.all()
		for task in tasks:
			menu += self.task_col(task)
		menu += f'</div>\n'
		return menu
	def task_col(self, hometask):
		col = f'<div class="col bg-light">\n'
		col += f'<span style="font-size: larger;">{hometask.name}</span>\n<ul>\n'
		tasks_ofhome = self.home.task_set.all()
		tasks_oftype = tasks_ofhome.filter(home_task=hometask).filter(start_time__month=self.date.month).order_by('-start_time')
		for task in tasks_oftype:
			col += self.task_case(task)
		col += '</ul>\n</div>\n'
		return col
	def task_case(self, task):
		case = f'<li>\n'
		case += f'{task.doer.user.first_name} <br/>'
		case += f'{task.start_time.strftime("%d-%m, %H:%M")} <br/><br />'
		case += f'</li>\n'
		return case

class TaskPlan():
	def __init__(self, home):
		self.home = home
		self.date = datetime.today()
	#formate 5 colonnes qui peuvent contenir chacune 1 case/bouton maison
	def task_plan(self):
		menu = f'<div class="row">\n'
		tasks = self.home.hometask_set.all()
		for task in tasks:
			menu += self.task_col(task)
		menu += f'</div>\n'
		return menu
	def task_col(self, hometask):
		col = f'<div class="col bg-light border">\n'
		col += f'<h3>{hometask.name}</h3>\n<ul>\n'
		tasks_ofhome = self.home.task_set.all()
		tasks_oftype = tasks_ofhome.filter(home_task=hometask).filter(start_time__month=self.date.month).order_by('-start_time')
		for task in tasks_oftype:
			col += self.task_case(task)
		col += '</ul>\n</div>\n'
		return col
	def task_case(self, task):
		case = f'<li>\n'
		case += f'{task.doer.user.first_name} <br/>'
		case += f'{task.start_time.strftime("%d-%m, %H:%M")} <br/><br />'
		case += f'</li>\n'
		return case

def gen_choices_users(home):
	h = Home.objects.get(pk=home)
	profiles = h.profile_set.all()
	choices = []
	for profile in profiles:
		choices.append([profile.user.pk, profile.user.first_name + ' ' + profile.user.last_name])
	return choices


def gen_choices_hometask(home):
	h = Home.objects.get(pk=home)
	profiles = h.hometask_set.all()
	choices = []
	for profile in profiles:
		choices.append([profile.pk, profile.name])
	return choices


def create_home_foyer(home):
	new = HomeTask(home=home, creator_id=1, name='Mettre la table', difficulty=1)
	new.save()
	new = HomeTask(home=home, creator_id=1, name='Lave-vaisselle', difficulty=2)
	new.save()
	new = HomeTask(home=home, creator_id=1, name='Poubelles', difficulty=2)
	new.save()
	new = HomeTask(home=home, creator_id=1, name='Ménage', difficulty=5)
	new.save()
	new = HomeTask(home=home, creator_id=1, name='Courses', difficulty=4)
	new.save()
	new = HomeTask(home=home, creator_id=1, name='Etendre le linge', difficulty=3)
	new.save()
	new = HomeTask(home=home, creator_id=1, name='Vaisselle', difficulty=3)
	new.save()