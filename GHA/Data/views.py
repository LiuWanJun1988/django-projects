from django.contrib import messages
from django.shortcuts import redirect
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from Data.models import *


import mysql.connector
# Create your views here.
conn = mysql.connector.Connect(host='localhost', user='root', password='asdfqwer', database='greyhound')
cursor = conn.cursor(buffered=True)



def login(request):
    template = loader.get_template('main/login.html')
    context = {}
    return HttpResponse(template.render(context, request))

def login_account(request):
    if request.method == "POST":
        name = request.POST['name']
        pwd = request.POST['password']
        try:
            user = User.objects.filter(name=name, password=pwd).values()[0]
        except:
            template = loader.get_template('main/login.html')
            context = {'login_error': "Username and Password are incorrect"}
            return HttpResponse(template.render(context, request))

        if user['permission'] == "admin":
            request.session['permission'] = "admin"
            request.session['user_id'] = user['id']
            return redirect('greyhound_data')

def greyhound_data(request):
    try:
        user_id = request.session['user_id']
        user = User.objects.filter(id=user_id).values()[0]
        template = loader.get_template('Data/greyhound_data.html')
        #query = """select * from city inner join (select data_race.city_id, data_race.date, data_race.number, data_race.name AS race_name, data_race.length, data_race.level, data_race.money, data_race.splits, data_race_data.box, data_race_data.rank, data_race_data.name, data_race_data.trainer, data_race_data.time, data_race_data.margin, data_race_data.split, data_race_data.in_run, data_race_data.weight, data_race_data.sire, data_race_data.dam, data_race_data.sp from data_race inner join data_race_data on data_race.id=data_race_data.race_id) as t_race on city.id=t_race.city_id order by date, number, states, city, rank"""
        #cursor.execute(query)
        #data = cursor.fetchall()
        city_list = City.objects.all().order_by('states', 'city').values()
        context = {
            "city_list": city_list
        }
        return HttpResponse(template.render(context, request))
    except Exception as e:
        print(e)
        request.session.flush()
        template = loader.get_template('main/login.html')
        context = {'login_error': "You have no permission to connect this link."}
        return HttpResponse(template.render(context, request))

def greyhound_search(request):
    if request.method == "POST":
        user_id = request.session['user_id']
        user = User.objects.filter(id=user_id).values()[0]
        city = request.POST["city"]
        start_date = request.POST["start_date"]
        end_date = request.POST["end_date"]
        temp1 = Race.objects.filter(city_id=city, date__range=[start_date, end_date]).values()
        temp2 = {}
        for item in temp1:
            temp = {}
            if str(item["date"]) not in temp2:
                temp2[str(item["date"])] = []
            temp["summary"] = item
            temp["data"] = list(Race_Data.objects.filter(race_id=item["id"]).order_by('race_id').values())
            temp2[str(item["date"])].append(temp)
        result = {key: temp2[key] for key in sorted(temp2, reverse=True)}#dict(sorted(temp2.items(), key=lambda item: item[1]))#{key: value for key, value in sorted(temp2.items(), key=lambda item: item[1])}
        context = {
            "data": result
        }
        return JsonResponse(context)





