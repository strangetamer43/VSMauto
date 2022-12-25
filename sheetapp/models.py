from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import HStoreField
from django.contrib.auth.models import User

# Create your models here.
class Company(models.Model):
	user = models.OneToOneField(User,null=True, blank=True, on_delete=models.CASCADE)
	company_name=models.CharField(max_length=100,null=True,blank=True)

	def __str__(self):
		return str(self.company_name)

# class Customer(models.Model):                        
# 	user = models.OneToOneField(User,null=True, blank=True, on_delete=models.CASCADE)
# 	company = models.ForeignKey(Company,null=True,blank=True,on_delete=models.CASCADE)
# 	name = models.CharField(max_length=200, null=True)
# 	phone = models.CharField(max_length=200, null=True)
# 	date_created = models.DateTimeField(auto_now_add=True, null=True)

# 	def __str__(self):
# 		return self.name

class Machine(models.Model):
	company=models.ForeignKey(Company,null=True,blank=True,on_delete=models.CASCADE)
	machine_name=models.CharField(max_length=100,null=True,blank=True)
	spreadsheet_id=models.CharField(max_length=100,null=True,blank=True)
	target = HStoreField(null=True,blank=True)
	shifts = models.IntegerField(null=True,blank=True)

	def __str__(self):
		return self.machine_name


class Order(models.Model):
	company=models.ForeignKey(Company,null=True,blank=True,on_delete=models.CASCADE)
	order_no=models.CharField(null=True,blank=True,max_length=100)
	
	def __str__(self):
		return self.order_no


class Process(models.Model):
	company=models.ForeignKey(Company,null=True,blank=True,on_delete=models.CASCADE)
	machine=models.ForeignKey(Machine,null=True,blank=True,on_delete=models.CASCADE)
	process_name=models.CharField(null=True,blank=True,max_length=100)

	def __str__(self):
		return self.process_name + '-' + str(self.company)

class Operator(models.Model):
	company = models.ForeignKey(Company,null=True,blank=True,on_delete=models.CASCADE)
	operator_no=models.CharField(null=True,blank=True,max_length=100)

	def __str__(self):
		return self.operator_no


class Productdetail(models.Model):
	company=models.ForeignKey(Company,null=True,blank=True,on_delete=models.CASCADE)
	date = models.DateField(null=True,blank=True)
	machine=models.ForeignKey(Machine,null=True,blank=True,on_delete=models.CASCADE)
	process=models.ForeignKey(Process,null=True,blank=True,on_delete=models.CASCADE)
	order=models.ForeignKey(Order,null=True,blank=True,on_delete=models.CASCADE)
	starttime=models.CharField(null=True,blank=True,max_length=100)
	endtime=models.CharField(null=True,blank=True,max_length=100)
	cycletime=models.CharField(null=True,blank=True,max_length=100)
	width=models.IntegerField(null=True,blank=True)
	thickness=models.DecimalField(null=True,blank=True,decimal_places=2,max_digits=5)
	weight=models.DecimalField(null=True,blank=True,decimal_places=2,max_digits=5)
	operator = ArrayField(models.CharField(null=True,blank=True,max_length=100),default=list,null=True,blank=True)

	def __str__(self):
		return str(self.machine)+str(self.process)

	class Meta:
    		ordering = ['id']


class Downtime(models.Model):
	company=models.ForeignKey(Company,null=True,blank=True,on_delete=models.CASCADE)
	date = models.DateField(null=True,blank=True)
	machine=models.ForeignKey(Machine,null=True,blank=True,on_delete=models.CASCADE)
	process=models.ForeignKey(Process,null=True,blank=True,on_delete=models.CASCADE)
	order=models.ForeignKey(Order,null=True,blank=True,on_delete=models.CASCADE)
	starttime=models.CharField(null=True,blank=True,max_length=100)
	endtime=models.CharField(null=True,blank=True,max_length=100)
	cycletime=models.CharField(null=True,blank=True,max_length=100)
	operator = ArrayField(models.CharField(null=True,blank=True,max_length=100),default=list,null=True,blank=True)