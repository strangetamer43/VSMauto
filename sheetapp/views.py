from django.shortcuts import render,redirect
from django.http import HttpResponse

#for sheets api
from django.views.generic import View
from google.oauth2.service_account import Credentials 
from googleapiclient.discovery import build
from .models import *
from .forms import *
import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = './credentials.json'

# Create the credentials object from the file
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Build the Google Sheets API client
service = build('sheets', 'v4', credentials=creds)

# Set the spreadsheet ID and sheet range
# spreadsheet_id = '1PK9LoJw_NbuQ122tQfgRHYgbtacrtN_cpa3Bakce70Q'
sheet_range = 'Sheet1!A1:Z'

# Retrieve the data from the Google Sheets API
# data = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_range).execute()


# Create your views here.
import csv, io
from django.shortcuts import render,redirect
from django.contrib import messages


from sheetapp.models import *
# Create your views here.
# one parameter named request

@unauthenticated_user
def registerPage(request):
	form = CreateUserForm()
	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			company = form.cleaned_data.get('company_name')
        
			Company.objects.create(user=user,company_name=company)
            # print(company)
            
			messages.success(request, 'Account was created for ' + user.username)

			return redirect('login')
		
	context = {'form':form}
	return render(request, 'register.html', context)

@unauthenticated_user
def loginPage(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password =request.POST.get('password')

		user = authenticate(request, username=username, password=password)

		if user is not None:
			login(request, user)
			return redirect('profile_upload')
		else:
			messages.info(request, 'Username or password is incorrect')

	context = {}
	return render(request, 'login.html', context)


def logoutUser(request):
	logout(request)
	return redirect('login')


@login_required(login_url='login')
def profile_upload(request):
    # declaring template
    template = "profile_upload.html"
    
    # prompt is a context variable that can have different values depending on their context
    prompt = {
        'order': 'Order of the CSV should be name, email, address,phone, profile',
              }
    # GET request returns the value of the data with the specified key.
    if request.method == "GET":
        return render(request, template, prompt)
    csv_file = request.FILES['file']
    # let's check if it is a csv file
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
    data_set = csv_file.read().decode('UTF-8')
    # setup a stream which is when we loop through each line we are able to handle a data in a stream
    io_string = io.StringIO(data_set)
    next(io_string)

    company=Company.objects.get(user=request.user)

    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        print(column)
        machine=Machine.objects.get(machine_name=column[7],company=company)
        d = column[0][:2]+column[0][3:5]+column[0][6:10]
        print(machine,column[1])    
        processes = Process.objects.get(machine=machine,process_name=column[6],company=company)
        date = datetime.datetime.strptime(d, '%m%d%Y').date()
        order,created_order=Order.objects.get_or_create(order_no=column[1],company=company)

        order=Order.objects.get(id=order.id)

        # convert the string into list
        operator_no = column[8].split(';')

        
        for i in operator_no:
            operator,created_op = Operator.objects.get_or_create(operator_no=i,company=company)
            # l.append(operator_no)

        if processes.process_name=='Down time':
                d,created =Downtime.objects.update_or_create(date=date,machine=machine,process=processes,order=order,starttime= row[4],
                endtime= column[5],operator= operator_no,company=company)
    
                st=d.starttime
                en=d.endtime
                sth,stm=map(int,st.split(':'))
                stm+=(60*sth)
                print(stm)
                enh,enm=map(int,en.split(":"))
                enm+=(60*enh)
                print(enm)
                ct=enm-stm
                d.cycletime=str(ct//60)+":"+str(ct%60)
                print(obj.cycletime)
                d.save()
                continue

        model_fields = {
                'date': date,
                'company': company,
                'machine': machine,
                'process': processes,
                'order':order,
                'starttime': column[4],
                'endtime': column[5],
                'weight': column[2],
                'thickness': column[3],
                'operator': operator_no,
            }
        
        obj, created = Productdetail.objects.update_or_create(**model_fields)
        print(obj,created)
        st=obj.starttime
        en=obj.endtime
        sth,stm=map(int,st.split(':'))
        stm+=(60*sth)
        print(stm)
        enh,enm=map(int,en.split(":"))
        enm+=(60*enh)
        print(enm)
        print(enm-stm)
        ct=enm-stm
        obj.cycletime=str(ct//60)+":"+str(ct%60)
        print(obj.cycletime)
        obj.save()
    context = {}
    return render(request, template, context)

@login_required(login_url='login')
def analysis(request,no):
    machine=Machine.objects.get(id=no)

    target=machine.target
    shifts=machine.shifts

    k = list(target.keys())[-1]
    target = int(target[k])
 

    target_per_shift = target/shifts
    target_per_hr = target_per_shift/8

    product=Productdetail.objects.filter(machine=machine)
    print(product)
    print("******************")
    
    total_cycle_time=0
    avg_cycle_time=0
    weight_produced=0
    change_over_time=0

    q = set(Productdetail.objects.filter(machine=machine).values_list('order').distinct())

    print("???GDS")
    print(q)
    no_of_pro = len(q)
    print(no_of_pro)

    s=set()
    w=0

    for i in product: 
        ct=i.cycletime
        enh,ctm=map(int,ct.split(":"))
        ctm+=(60*enh)
        if i.order not in s:
            s.add(i.order)
            w+=i.weight
        if i.process.process_name!='Running':
            change_over_time+=ctm
        print(ctm)
        total_cycle_time+=ctm
        avg_process=0

    print(total_cycle_time)
    print(w)

    d=Downtime.objects.filter(machine=machine)
    total=0
    for i in d:
        st=i.cycletime
        sth,stm=map(int,st.split(':'))
        ctm=stm+sth*60
        total+=ctm

    if total_cycle_time>=60:
        avg_unit_per_hr = no_of_pro/(total_cycle_time/60)
    cycle_time_per_ton=total_cycle_time/w
    takt_time=total_cycle_time/target
    eff=(total_cycle_time/change_over_time)*100
    print(no_of_pro,total_cycle_time,change_over_time,avg_process,takt_time,eff,w,cycle_time_per_ton)
    context={'no_of_pro':no_of_pro,'total_cycle_time':total_cycle_time,'change_over_time':change_over_time,
    'avg_unit_per_hr':avg_unit_per_hr,'takt_time':takt_time,'eff':eff,'weight_produced':w,
    'cycle_time_per_ton':cycle_time_per_ton,'target':target,'target_per_shift':target_per_shift,'target_per_hr':target_per_hr,'total':total}
    return render(request,'base.html',context)


@login_required(login_url='login')
def operator_analysis(request,no):
    operator=Operator.objects.get(operator_no=no,company=request.user.company)
    print(operator)
    print(type(no))
    # product=Productdetail.objects.filter(operator__overlap=[no])
    # print(product)
    total_cycle_time=0

    product="a"

    if request.method=='POST':
        from_date=request.POST['from']
        to=request.POST['to']
        print(from_date,to)
        product=Productdetail.objects.filter(operator__overlap=[no],date__range=[from_date,to],company=request.user.company)
        p = set(product.values_list('order').distinct())
        print(product)
        s = set()
        w=0
        t=0
        indexj=0
        d=set()
        for i in product:
            # w+=i.weight
            # if i.order not in s:
            #     s.add(i.order)
            #     w+=i.weight
            if i.date not in d:
                s=set()
                d.add(i.date)
                target = i.machine.target
                k = list(target.keys())
                for j in range(len(k)):
                    if i.date<=datetime.datetime.strptime(k[j],'%Y-%m-%d').date():
                        print(i.date,k[j])
                        indexj=j
                        break
                print(indexj)
                if indexj>0:
                    target = int(target[k[indexj-1]])
                    print(k[indexj-1])
                else:
                    target = int(target[k[indexj]])
                    print(k[indexj],target)
        
                t+=target
                print('t=',t)
            if i.order not in s:
                s.add(i.order)
                w+=i.weight
            
        print(t)
        print(w)
        context={'product':product,'w':w,'t':t,'p':len(p)}
        return render(request,'operator.html',context)

    return render(request,'operator.html')


@login_required(login_url='login')
def show_data(request,mac=None):
    company=Company.objects.get(user=request.user)
    ma=Machine.objects.get(id=mac,company=company)
    spreadsheet_id=ma.spreadsheet_id
    # Retrieve the data from the Google Sheets API
    data = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_range).execute()
    # Pass the data to the template as context
    values = data.get('values', [])

    # to check if the data is already in the database
    if not values:
        print('No data found.')
    else:
        company=Company.objects.get(user=request.user)
        for row in values:
            print(row)
            machine = Machine.objects.get(machine_name=row[7], company=company)
            d = row[0][:2]+row[0][3:5]+row[0][6:10]
            print(machine,row[1])
            processes = Process.objects.get(process_name=row[6], machine=machine, company=company)
        
            date = datetime.datetime.strptime(d, '%m%d%Y').date()
            order,created_order=Order.objects.get_or_create(order_no=row[1],company=company)

            order=Order.objects.get(id=order.id)

            # convert the string into list
            operator_no = row[8].split(';')

            for i in operator_no:
                operator,created_op = Operator.objects.get_or_create(operator_no=i,company=company)


            # convert the string into list
            operator_no = row[8].split(';')
            
            if processes.process_name=='Down time':
                d,created =Downtime.objects.update_or_create(date=date,machine=machine,process=processes,order=order,starttime= row[4],
                endtime= row[5],operator= operator_no,company=company)
    
                st=d.starttime
                en=d.endtime
                sth,stm=map(int,st.split(':'))
                stm+=(60*sth)
                print(stm)
                enh,enm=map(int,en.split(":"))
                enm+=(60*enh)
                print(enm)
                ct=enm-stm
                d.cycletime=str(ct//60)+":"+str(ct%60)
                print(obj.cycletime)
                d.save()
                continue

            # Map the columns to the Django model fields
            model_fields = {
                'date': date,
                'company': company,
                'machine': machine,
                'process': processes,
                'order':order,
                'starttime': row[4],
                'endtime': row[5],
                'weight': row[2],
                'thickness': row[3],
                'operator': operator_no,
            }

            obj, created_product = Productdetail.objects.update_or_create(**model_fields)
            print(obj,created_product)
            st=obj.starttime
            en=obj.endtime
            sth,stm=map(int,st.split(':'))
            stm+=(60*sth)
            print(stm)
            enh,enm=map(int,en.split(":"))
            enm+=(60*enh)
            print(enm)
            print(enm-stm)
            ct=enm-stm
            obj.cycletime=str(ct//60)+":"+str(ct%60)
            print(obj.cycletime)
            obj.save()
        context = {'data': data}
        return render(request, 'test_show.html', context)

    return render(request, 'test_show.html', {'data': data})


@login_required(login_url='login')
def machine_details(request):
    if request.method=="POST":
        machine=request.POST.get('machine')
        sheet=request.POST.get('excel')
        date = datetime.datetime.now().date()
        print(date)
        target=request.POST.get('target')
        shifts=request.POST.get('shifts')
        m=Machine(machine_name=machine,spreadsheet_id=sheet,target={str(date):target},shifts=shifts,company=request.user.company)
        m.save()
        print(m)
    return render(request,'detail_forms.html')


@login_required(login_url='login')
def process_details(request,machine):
    m=Machine.objects.get(id=machine)
    c=Process.objects.filter(machine=m)
    if request.method=='POST':
        process=request.POST.get('process')
        p=Process(machine=m,process_name=process,company=request.user.company)
        p.save()
        return redirect('machine_view')
        # return render(request,temp)
    return render(request,'process_detail_forms.html',{'process':c})


@login_required(login_url='login')
def target(request,id):
    machine=Machine.objects.get(id=id)
    date = datetime.datetime.now().date()
    target = machine.target
    shifts = machine.shifts
    print(target)
    k = list(target.keys())[-1]
    target = target[k]
 

    if request.method == 'POST':
        target = request.POST.get('target')
        shifts = request.POST.get('shifts')
        machine.target[date] = target
        machine.shifts = shifts
        machine.save()
        print(target, shifts)
        return redirect('machine_view')
    return render(request, 'target.html', {'target': target, 'shifts': shifts})


@login_required(login_url='login')
def show_operators(request):
    op=Operator.objects.filter(company=request.user.company)
    return render(request,'show_operator.html',{'operators':op})

@login_required(login_url='login')
def machine_view(request):
    m=Machine.objects.filter(company=request.user.company)
    return render(request,'machines.html',{'machines':m})

@login_required(login_url='login')
def show_order(request):
    orde=Order.objects.filter(company=request.user.company)
    return render(request,'show_order.html',{'orders':orde})


@login_required(login_url='login')
def show_lead_time(request):
    pass

@login_required(login_url='login')
def fun(request,d1,st,d2,en):
    d=d1-d2
    d=d.days
    print("cdbcb")
    print(d)
    sth,stm=map(int,st.split(':'))
    stm+=(60*sth)
    enh,enm=map(int,en.split(":"))
    enm+=(60*enh)
    # print(enm)
    # print(enm-stm)
    ct=abs(enm-stm)

    d=24*60*d+ct

    print('days=',d)
    return d//(60*24)

@login_required(login_url='login')  
def avg_lead_time(request):
    o=Order.objects.filter(company=request.user.company)
    leadtime=0
    for i in o:
        p=Productdetail.objects.filter(order=i)
        for j in range(len(p)-1):
            if p[j].machine!=p[j+1].machine:
                # print(lead_time)
                leadtime+=(fun(p[j+1].date,p[j+1].starttime,p[j].date,p[j].endtime))
    return HttpResponse(leadtime//len(o))

@login_required(login_url='login')
def lead_time(request,id):
    print("||||||||||||||||")
    print(id)
    o=Order.objects.get(id=id)
    p=Productdetail.objects.filter(order=o)
    leadtime=0

    for i in range(len(p)-1):
        print(i)
        if p[i].machine!=p[i+1].machine:
            # print(lead_time)
            leadtime+=(fun(request,p[i+1].date,p[i+1].starttime,p[i].date,p[i].endtime))
    return HttpResponse(leadtime)


# It retrieves the Order object that has the order number passed in as a parameter.
# The function then filters the Productdetail objects to only include those that are associated with the Order object. 
# It initializes a variable called leadtime to 0.

# The function then iterates over the filtered Productdetail objects and calculates the lead time between each pair 
# of Productdetail objects. If the machines associated with the current and next Productdetail objects are not 
# the same, the lead time is calculated by calling the fun function and passing in the date and time values for 
# the current and next Productdetail objects. The calculated lead time is then added to the leadtime variable.

# Finally, the function returns an HTTP response with the calculated lead time.

def downtime_calc(request):
    if request.method=='POST':
        from_date=request.POST['from']
        to=request.POST['to']
        print(from_date,to)
        d=Downtime.objects.filter(date__range=[from_date,to])
        total=0
        for i in d:
            st=i.cycletime
            sth,stm=map(int,st.split(':'))
            ctm=stm+sth*60
            total+=ctm
        return render(request,'downtime.html',{'total':total,'dt':d})
    return render(request,'downtime.html')

