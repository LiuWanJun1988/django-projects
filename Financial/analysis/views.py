import csv
from datetime import datetime

from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from Financial import settings


# Create your views here.
def login(request):
    template = loader.get_template('landingPage/login.html')
    context = {}

    return HttpResponse(template.render(context, request))

def analysis(request):
    template = loader.get_template('pages/dashboard.html')
    context = {}
    return HttpResponse(template.render(context, request))

def chart_display(request):
    template = loader.get_template('pages/dashboard.html')
    context = {}

    if request.method == "POST":
        start_date = request.POST['start_date']
        period = request.POST['period']
        bull_percent = request.POST['min_raise']
        bear_percent = request.POST['min_fall']
        total_data, date_data = get_test_data(start_date)
        #print(total_data)
        normal_data, table_data = get_graph_data(total_data, int(period), float(bull_percent), float(bear_percent))
        #print(normal_data)
        #print(date_data)
        context = {
            'normal_data': normal_data,
            'table_data': table_data,
            #'bear_data': bear_data,
            'date_data': date_data
        }

    #return HttpResponse(template.render(context, request))
    return JsonResponse(context)

def get_test_data(start_date):
    total_data = list()
    date_data = list()
    dow_data_file_path = settings.DATA_ROOT + '\dow_data.csv'
    end_date = start_date[:len(start_date)-4] + str(int(start_date[len(start_date)-4:]) + 30)
    end_date_date = datetime.strptime(end_date, '%m/%d/%Y')
    start_date_date = datetime.strptime(start_date, '%m/%d/%Y')
    with open(dow_data_file_path) as f:
        readCSV = csv.reader(f, delimiter=',')
        csv_data = list(readCSV)
        for i in range(1, len(csv_data)):
            now_date = datetime.strptime(csv_data[i][0], '%m/%d/%Y')
            if now_date >= start_date_date and now_date <= end_date_date:
                total_data.append([csv_data[i][0], float(csv_data[i][1])])
                date_data.append(csv_data[i][0])

    return total_data, date_data

def get_graph_data(data, period, bull_percent, bear_percent):
    data_status = ""
    bull_data = list()
    bear_data = list()
    normal_data = list()

    result_data = list()
    table_result = list()
    bull_result = list()
    bear_result = list()
    start_index = 0
    data_limit = len(data) - period + 1
    while data_limit > start_index:
        end_index = start_index + period - 1
        if (data[end_index][1] - data[start_index][1]) / data[start_index][1] * 100 >= bull_percent:
            for i in range(start_index, end_index + 1):
                #bull_data.append(data[i])
                bull_data.append({'x': i, 'y': data[i][1], 'name': data[i][0]})
            result_data.append({'data': bull_data, 'color': '#FF0000'})
            table_result.append({'data': bull_data, 'color': '#FF0000'})
            bull_data = []

            if data_status == "normal":
                normal_data.append({'x': start_index, 'y': data[start_index][1], 'name': data[start_index][0]})
                result_data.append({'data': normal_data, 'color': '#000000'})
                normal_data = []
            start_index = end_index
            data_status = "bull"
        elif (data[start_index][1] - data[end_index][1]) / data[start_index][1] * 100 >= bear_percent:
            for i in range(start_index, end_index + 1):
                #bear_data.append(data[i])
                bear_data.append({'x': i, 'y': data[i][1], 'name': data[i][0]})
            result_data.append({'data': bear_data, 'color': '#0000FF'})
            table_result.append({'data': bear_data, 'color': '#0000FF'})
            bear_data = []

            if data_status == "normal":
                normal_data.append({'x': start_index, 'y': data[start_index][1], 'name': data[start_index][0]})
                result_data.append({'data': normal_data, 'color': '#000000'})
                normal_data = []
            start_index = end_index
            data_status = "bear"
        else:
            #normal_data.append(data[start_index])
            normal_data.append({'x': start_index, 'y': data[start_index][1], 'name': data[start_index][0]})
            if len(normal_data) >= 50:
                result_data.append({'data': normal_data, 'color': '#000000'})
                normal_data = []
                normal_data.append({'x': start_index, 'y': data[start_index][1], 'name': data[start_index][0]})
            start_index += 1
            data_status = "normal"

    return result_data, table_result



