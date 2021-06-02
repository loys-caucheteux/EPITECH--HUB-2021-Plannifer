from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from payments import PurchasedItem
from payments.models import BasePayment

ADRESS = 'https://plannifer.herokuapp.com/'

class Home(models.Model):
    creator = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(name="name", max_length=50)
    class Meta:
        verbose_name = ('Home')
        verbose_name_plural = ('Homes')
    def __str__(self):
        return '%s' %(self.name)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    homes = models.ManyToManyField(Home)
    stars = models.IntegerField(name="stars")
    is_premium = models.BooleanField(name="is_premium", default=False)
    class Meta:
        verbose_name = ('Profile')
        verbose_name_plural = ('Profiles')
    def __str__(self):
        return "%s the user" % self.user.username

class HomeTask(models.Model):
    home = models.ForeignKey(Home, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(name="name", max_length=50)
    difficulty = models.IntegerField(default=1, null=True)
    def __str__(self):
        return '%s %s' %(self.name, self.home)
    class Meta:
        verbose_name = ("HomeTask")
        verbose_name_plural = ("HomeTasks")


class Spent(models.Model):
    home = models.ForeignKey(Home, on_delete=models.CASCADE)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(name="title", max_length=100)
    amount = models.DecimalField(name = 'amount', max_digits=7, decimal_places=2)

class Task(models.Model):
    title = models.CharField(name="title", max_length=50)
    description = models.TextField(name="description", null=True, max_length=500)
    doer = models.ForeignKey(Profile, related_name='doer', on_delete=models.CASCADE, null=True)
    creator = models.ForeignKey(Profile, related_name='creator', on_delete=models.CASCADE, null=True)
    home = models.ForeignKey(Home, on_delete=models.CASCADE)
    home_task = models.ForeignKey(HomeTask, on_delete=models.CASCADE, null=True)
    spent = models.OneToOneField(Spent, on_delete=models.SET_NULL, null=True)
    difficulty =  models.IntegerField(name="difficulty")
    start_time = models.DateTimeField(name="start_time")
    end_time = models.DateTimeField(name="end_time")
    denonceur = models.ForeignKey(Profile, related_name='denonceur', on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return f'id : {self.pk} {self.title} doer : {self.doer} created by {self.creator}'
    class Meta:
        verbose_name = ('Task')
        verbose_name_plural = ('Tasks')

class Payment(BasePayment):
    def get_failure_url(self):
        return f'{ADRESS}orders/failure'

    def get_success_url(self):
        return f'{ADRESS}orders/sucess'

    def get_purchased_items(self):
        pass
    class Meta:
        verbose_name = ('Payment')
        verbose_name_plural = ('Payments')