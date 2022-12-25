from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(Machine)

admin.site.register(Order)

admin.site.register(Process)

admin.site.register(Operator)

admin.site.register(Productdetail)

admin.site.register(Company)

admin.site.register(Downtime)

