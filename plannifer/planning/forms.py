from django import forms
from django.forms.utils import ErrorList
from django.contrib.auth.forms import AuthenticationForm
from .utils import gen_choices_users, gen_choices_hometask
from .models import User, Profile

class ParagraphErrorList(ErrorList):
    def __str__(self):
        return self.as_divs()
    def as_divs(self):
        if not self: return ''
        return '<div class="errorlist">%s</div>' % ''.join(['<p class="small error">%s</p>' % e for e in self])

class MyLoginForm(AuthenticationForm):
    def __init__(self,*args, **kwargs):
        super(MyLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(
        label='Username',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E-mail'})
    )
    password = forms.CharField(
        label='Password',
        max_length=100,
        required=True,
        widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

class RegisterUserForm(forms.Form):
    mail = forms.EmailField(
        label='Email',
        max_length=100,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control mt-2', 'placeholder': 'E-mail'})
        )
    name = forms.CharField(
        label='Name',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control mt-2', 'placeholder': 'First Name'})
        )
    surname = forms.CharField(
        label='Surname',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control mt-2', 'placeholder': 'Last Name'})
        )
    pseudo = forms.CharField(
        label='Pseudo',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control mt-2',  'placeholder': 'Username'})
        )
    pwd = forms.CharField(
        label='Password',
        max_length=100,
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control mt-2', 'placeholder': 'Password'})
    )

class AddHomeForm(forms.Form):
    name = forms.CharField(
        label='Name',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Home Name...'})
    )

class AddUserForm(forms.Form):
    username = forms.CharField(
        label='username',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'id': 'inputPassword6',
         'class': 'form-control',
         'placeholder': 'Add user (input : username)',
         'aria-describedby':"passwordHelpInline"})
    )

class AddTaskForm(forms.Form):
    name = forms.CharField(
        label='name',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'id': 'clear_form',
        'class': 'form-control',
        'placeholder': 'Task Name...',
        'aria-describedby': 'task_difficulty'})
    )
    difficulty = forms.IntegerField(
        label='difficulty',
        min_value=1,
        max_value=5,
        required=True,
        widget=forms.NumberInput(attrs={'id': 'task_difficulty',
        'class': 'form-control',
        'placeholder': 'Stars',
        'aria-describedby': 'btn-task-v'})
    )

class CreateTaskForm(forms.Form):
    def __init__(self, *args, home, **kwargs):
        self.home = home
        super(CreateTaskForm, self).__init__(*args, **kwargs)
        self.fields['doer'] = forms.ChoiceField(label='doer', choices = gen_choices_users(home=home), required=True)
        self.fields['home_task'] = forms.ChoiceField(label='home_task', choices = gen_choices_hometask(home=home), required=True)

    title = forms.CharField(
        label='title',
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'})
        )
    description = forms.CharField(
        label='description',
        max_length=140,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'})
        )
    start_time = forms.DateTimeField(
        label='start_time',
        required=True,
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'Start time', 'autocomplete': 'off'})
        )
    end_time = forms.DateTimeField(
        label='end_time',
        required=True,
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'End time', 'autocomplete': 'off'})
    )
    spent = forms.FloatField(
    max_value=100000.0,
    min_value=0,
    label='spent',
    required=False,
    widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(facultative) cost', 'autocomplete': 'off'}))
    class Meta:
        fields = ('title', 'description', 'doer', 'home_task', 'start_time', 'end_time', 'spent')
        
class EditTaskForm(forms.Form):
    def __init__(self, *args, task, **kwargs):
        self.task = task
        self.home = task.home
        super(EditTaskForm, self).__init__(*args, **kwargs)
        self.fields['title'] = forms.CharField(
            label='title',
            max_length=50,
            required=True,
            widget=forms.TextInput(attrs={'class': 'form-control', 'value': f'{self.task.title}','placeholder': 'Title'})
            )
        self.fields['description'] = forms.CharField(
            label='description',
            max_length=140,
            required=False,
            widget=forms.TextInput(attrs={'class': 'form-control', 'value': f'{self.task.description}', 'placeholder': 'Description'})
            )
        self.fields['start_time'] = forms.DateTimeField(
            label='start_time',
            required=True,
            input_formats=['%d/%m/%Y %H:%M'],
            widget=forms.DateTimeInput(attrs={'class': 'form-control', 'value': f'{self.task.start_time}', 'placeholder': 'Start time', 'autocomplete': 'off'})
            )
        self.fields['end_time'] = forms.DateTimeField(
            label='end_time',
            required=True,
            input_formats=['%d/%m/%Y %H:%M'],
            widget=forms.DateTimeInput(attrs={'class': 'form-control', 'value': f'{self.task.end_time}', 'placeholder': 'End time', 'autocomplete': 'off'})
        )
        if self.task.spent != None:
            self.fields['spent'] = forms.FloatField(
            max_value=100000.0,
            min_value=0,
            label='spent',
            required=False,
            widget=forms.TextInput(attrs={'class': 'form-control', 'value': f'{task.spent.amount} €', 'placeholder': '(facultative) cost', 'autocomplete': 'off'}))
    class Meta:
        fields = ('title', 'description', 'start_time', 'end_time', 'spent')


class SelectMonthForm(forms.Form):
    date = forms.DateTimeField(
        label='date',
        required=True,
        input_formats=['%m/%Y'],
        widget=forms.DateTimeInput(attrs={'onchange': 'write_date()', 'class': 'date_x dropdown-item form-control', 'placeholder': 'example: 4/2021', 'autocomplete': 'off'})
        )