from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django import forms

# Create Form
class CreateUserForm(UserCreationForm):
	company_name = forms.CharField(max_length=100,required=True)
	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2','company_name']