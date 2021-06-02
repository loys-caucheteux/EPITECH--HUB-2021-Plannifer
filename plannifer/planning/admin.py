from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
# Register your models here.

from .models import *

admin.site.register(Task)
admin.site.register(Home)
admin.site.register(Profile)