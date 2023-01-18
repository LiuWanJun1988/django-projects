from django.shortcuts import render
#from __future__ import unicode_literals
import os
#from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.conf import settings

import os
import pandas_datareader as pdr
import csv
import tulipy
import numpy as np
import requests


from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.http import JsonResponse
from Option_Trading import settings
import json
import datetime
import time

from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from django.urls import reverse
#from django.urls import reverse
#from ib.opt import ibConnection, message, Connection
#from ib.ext.Contract import Contract
#from ibapi.client import EClient
#from ibapi.wrapper import EWrapper
#from ibapi.contract import Contract

from broker_app.models import Account
from broker_app.models import Security
# Create your views here.

class data_model:
    def __init__(self, user_id, security_id):
        self.user_id = user_id
        self.security_id = security_id
        self.history_data = []
        self.bar_data = []
        self.sma_data = []
        self.ratio_data =[]
        self.atr_data = []
        self.long_short_data = []
        self.last_price = {}

        self.get_history_data()
    def get_history_data(self):
        self.security = Security.objects.filter(id=self.security_id, user_id=self.user_id).values()[0]
        self.symbol_list = self.security['symbols'].split(",")
        self.rest_date = get_rest_trading_days(self.security['expire_date'])
        start_date = self.security['expire_date'] - datetime.timedelta(days=(int((self.rest_date + self.security['data_size']) / 5 + 10) * 7))
        if self.security['type'] == "STOCK":
            for symbol in self.symbol_list:
                try:
                    temp_data = pdr.get_data_yahoo(symbol, start=start_date, end=datetime.datetime.today())
                    del temp_data['Volume']
                    del temp_data['Adj Close']
                    date_list = temp_data.index.tolist()
                    data_size = len(date_list)
                    if data_size > self.rest_date + self.security['data_size']:
                        temp_data = temp_data.iloc[data_size - self.rest_date - self.security['data_size']:]
                    # temp_dict = temp_data.to_dict()
                    # print(temp_data)
                    self.history_data = temp_data
                    if self.rest_date > 0:
                        data = {
                            "Open": list(tulipy.sma(temp_data['Open'].values, self.rest_date)),
                            "High": list(tulipy.sma(temp_data['High'].values, self.rest_date)),
                            "Low": list(tulipy.sma(temp_data['Low'].values, self.rest_date)),
                            "Close": list(tulipy.sma(temp_data['Close'].values, self.rest_date))
                        }
                    else:
                        data = {
                            "Open": list(temp_data['Open'].values),
                            "High": list(temp_data['High'].values),
                            "Low": list(temp_data['Low'].values),
                            "Close": list(temp_data['Close'].values)
                        }
                    self.bar_data.append({
                        "symbol": symbol,
                        "data": data
                    })
                    self.sma_data.append({
                        "symbol": symbol,
                        "data": data['Close']
                    })
                    self.last_price[symbol] = temp_data['Close'].values[-1]
                except Exception as e:
                    print(e)
                    pass

            #print(self.last_price)
            #print([item['symbol'] for item in self.bar_data])
            for i in range(len(self.sma_data)):
                bbb = []
                if i > 0:
                    for k in range(i):
                        bbb.append(0)
                bbb.append(1.0)
                for j in range(i + 1, len(self.sma_data)):
                    aaa = np.corrcoef(self.sma_data[i]['data'], self.sma_data[j]['data'])
                    bbb.append(aaa[0][1])
                self.ratio_data.append(bbb)

            for symbol_data in self.bar_data:
                short_data = []
                long_data = []
                for i in range(len(self.sma_data[0]['data'])):
                    if i > 0:
                        short = max(symbol_data['data']['High'][i] - symbol_data['data']['Close'][i],
                                    abs(symbol_data['data']['High'][i] - symbol_data['data']['Close'][i - 1]),
                                    abs(symbol_data['data']['Low'][i] - symbol_data['data']['Close'][i - 1]))
                    else:
                        short = symbol_data['data']['High'][i] - symbol_data['data']['Low'][i]
                    long = abs(float(symbol_data['data']['Open'][i] - symbol_data['data']['Close'][i]))
                    short_data.append(float(format(short, '.2f')))
                    long_data.append(float(format(long, '.2f')))
                self.long_short_data.append({
                    "symbol": symbol_data['symbol'],
                    "data": {
                        "short": short_data,
                        "long": long_data
                    }
                })
            short_temp = []
            long_temp = []
            for item in self.long_short_data:
                short_min = min(item['data']['short'])
                short_max = max(item['data']['short'])
                long_min = min(item['data']['long'])
                long_max = max(item['data']['long'])
                #print("aaaaaaaaaaaaaaaa")
                #print(item['data']['short'])
                #print(item['data']['long'])
                short_price_unit = (short_max - short_min) / 90
                long_price_unit = (long_max - long_min) / 90
                short_last = item['data']['short'][-1]
                long_last = item['data']['long'][-1]
                try:
                    if short_last == short_max:
                        short_percent = 95
                    else:
                        short_percent = (short_last - short_min) / (short_max - short_min) * 90 + 5
                except:
                    short_percent = 5.0
                try:
                    if long_last == long_max:
                        long_percent = 95
                    else:
                        long_percent = (long_last - long_min) / (long_max - long_min) * 90 + 5
                except:
                    long_percent = 5.0
                #print("cccccccccccccccccccccccc")
                short_temp.append(short_percent)
                long_temp.append(long_percent)
                self.atr_data.append({
                    "symbol": item['symbol'],
                    "short": {
                        "min": short_min,
                        "max": short_max,
                        "price_percent": format(short_price_unit, '.2f'),
                        "last": short_last,
                        "last_percent": format(short_percent, '.2f'),

                    },
                    "long":{
                        "min": long_min,
                        "max": long_max,
                        "price_percent": format(long_price_unit, '.2f'),
                        "last": long_last,
                        "last_percent": format(long_percent, '.2f')
                    },
                    "last_price": format(self.last_price.get(item['symbol']), '.2f')
                })
            self.short_min = format(min(short_temp), '.2f')
            self.short_max = format(max(short_temp), '.2f')
            self.long_min = format(min(long_temp), '.2f')
            self.long_max = format(max(long_temp), '.2f')
            #print(self.atr_data)

        else:
            return None


def get_symbol_list():
    stock_list = []
    cfd_list = []
    cfd_index_list = []
    forex_list = []
    ticker_list = []
    stock_str = ""
    cfd_str = ""
    cfd_index_str = ""
    forex_str = ""

    stock_path = settings.MEDIA_ROOT + "/saxo/stock"
    cfd_path = settings.MEDIA_ROOT + "/saxo/cfd"
    cfd_index_path = settings.MEDIA_ROOT + "/saxo/cfd_index"
    forex_path = settings.MEDIA_ROOT + "/saxo/" + "forex"

    for file in os.listdir(stock_path):
        if file.endswith(".txt"):
            try:
                with open(os.path.join(stock_path, file)) as ticker_file:
                    data = json.load(ticker_file)
                ticker_list = data['ticker']
                for ticker in ticker_list.split(','):
                    if ticker not in stock_list:
                        stock_list.append(ticker)
                        if stock_str =="":
                            stock_str += ticker
                        else:
                            stock_str += "," + ticker
            except Exception as e:
                print(file)

    for file in os.listdir(cfd_path):
        if file.endswith(".txt"):
            try:
                with open(os.path.join(cfd_path, file)) as ticker_file:
                    data = json.load(ticker_file)
                ticker_list = data['ticker']
                for ticker in ticker_list.split(','):
                    if ticker not in cfd_list:
                        cfd_list.append(ticker)
                        if cfd_str =="":
                            cfd_str += ticker
                        else:
                            cfd_str += "," + ticker
            except Exception as e:
                print(file)

    for file in os.listdir(cfd_index_path):
        if file.endswith(".txt"):
            try:
                with open(os.path.join(cfd_index_path, file)) as ticker_file:
                    data = json.load(ticker_file)
                ticker_list = data['ticker']
                for ticker in ticker_list.split(','):
                    if ticker not in cfd_index_list:
                        cfd_index_list.append(ticker)
                        if cfd_index_str =="":
                            cfd_index_str += ticker
                        else:
                            cfd_index_str += "," + ticker
            except Exception as e:
                print(file)

    for file in os.listdir(forex_path):
        if file.endswith(".txt"):
            try:
                with open(os.path.join(forex_path, file)) as ticker_file:
                    data = json.load(ticker_file)
                ticker_list = data['ticker']
                for ticker in ticker_list.split(','):
                    if ticker not in forex_list:
                        forex_list.append(ticker)
                        if forex_str =="":
                            forex_str += ticker
                        else:
                            forex_str += "," + ticker
            except Exception as e:
                print(file)

    return stock_str, cfd_str, cfd_index_str, forex_str

def get_rest_trading_days(expire_date):
    today_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=6)).strftime("%Y-%m-%d")
    time_now = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=6)).strftime("%H:%M:%S")
    open_time = "09:30:00"
    rest_date = np.busday_count(today_date, expire_date)
    time_delta = datetime.datetime.strptime(open_time, "%H:%M:%S") - datetime.datetime.strptime(time_now, "%H:%M:%S")
    if time_delta.days == 0:
        rest_date += 1
    return rest_date

def write_to_json(data_model, security_id):
    result = []
    atr_data = data_model.atr_data

    for item in atr_data:
        temp_data = {}
        temp_data['symbol'] = item['symbol']
        temp_data['last_price'] = str(item['last_price'])
        temp_data['short_min'] = str(item['short']['min'])
        temp_data['short_max'] = str(item['short']['max'])
        temp_data['short_price_percent'] = item['short']['price_percent']
        temp_data['short_last'] = str(item['short']['last'])
        temp_data['short_last_percent'] = item['short']['last_percent']
        temp_data['long_min'] = str(item['long']['min'])
        temp_data['long_max'] = str(item['long']['max'])
        temp_data['long_price_percent'] = item['long']['price_percent']
        temp_data['long_last'] = str(item['long']['last'])
        temp_data['long_last_percent'] = item['long']['last_percent']
        result.append(temp_data)

    result_json = {"aaData": result}
    path = settings.MEDIA_ROOT + "/security/security_" + str(security_id) + ".json"

    #print(path)
    with open(path, 'w', encoding="utf-8") as f:
        json.dump(result_json, f)


############## URL Request ##################
def login(request):
    template = loader.get_template('pages/landingpage/login.html')
    context = {}
    return HttpResponse(template.render(context, request))

def login_account(request):
    if request.method == "POST":
        user_name = request.POST['user_name']
        password = request.POST['password']
        try:
            #id = Account.objects.filter(user_id=user_name, password=password).values("id")
            #status = Account.objects.filter(user_id=user_name, password=password).values("status")
            #expire_date = Account.objects.filter(user_id=user_name, password=password).values("expire_date")
            account = Account.objects.filter(user_id=user_name, password=password).values()[0]
        except:
            template = loader.get_template('pages/landingpage/login.html')
            context = {'login_error': "Username and Password are incorrect"}
            return HttpResponse(template.render(context, request))
        if account['user_id'] != [] and account['status'] == "enable":
            today = datetime.date.today()
            if account['expire_date'] > today:
                request.session.flush()
                permission = account['permission']
                request.session['permission'] = permission
                request.session['user_id'] = account['id']
                #request.session.set_expiry(600)
                #s_account = session_account(account['id'])
                #request.session['account'] = s_account
                if permission == 1:
                    #return HttpResponseRedirect(reverse('admin_dashboard'))
                    return redirect('admin_dashboard', id='all')
                elif permission == 2:
                    #return HttpResponseRedirect(reverse('dashboard', id='all'))
                    return redirect('dashboard', id='all')
            else:
                template = loader.get_template('pages/landingpage/login.html')
                context = {'login_error': "Your account are expired. Please ask administrator."}
                return HttpResponse(template.render(context, request))

        else:
            template = loader.get_template('pages/landingpage/login.html')
            context = {'login_error': "Username and Password are incorrect"}
            return HttpResponse(template.render(context, request))

def dashboard(request, id):
    try:
        permission = request.session['permission']
        user_id = request.session['user_id']
        today_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=6)).strftime("%Y-%m-%d")
        if request.session['permission'] == 2:
            account = Account.objects.filter(id=user_id).values()[0]
            if id == "all":
                template = loader.get_template('pages/user/html/dashboard.html')
                stock_list, cfd_list, cfd_index_list, forex_list = get_symbol_list()
                temp_list = Security.objects.filter(user_id=user_id).values()
                security_list = []
                for security in temp_list:
                    rest_date = get_rest_trading_days(security['expire_date'])
                    symbol_count = len(security['symbols'].split(","))
                    if rest_date > 0:
                        security['rest_days'] = rest_date
                    else:
                        security['rest_days'] = "Expired"
                    security['symbol_count'] = symbol_count
                    security_list.append(security)
                request.session['permission'] = 1
                request.session['user_id'] = request.session['user_id']
                context = {
                    "today": today_date,
                    "security_list": security_list,
                    "stock_list": stock_list,
                    "cfd_list": cfd_list,
                    "cfd_index_list": cfd_index_list,
                    "forex_list": forex_list
                }
                return HttpResponse(template.render(context, request))
            elif id == "filter":
                security_id = request.POST['security_id']
                security = Security.objects.filter(id=security_id, user_id=user_id).values()[0]
                data = data_model(user_id, security_id)
                template = loader.get_template('pages/user/html/dashboard_view.html')
                short_min = request.POST['short_min']
                short_max = request.POST['short_max']
                long_min = request.POST['long_min']
                long_max = request.POST['long_max']
                operator = request.POST['operator']
                result = []
                atr_data = data.atr_data
                for item in atr_data:
                    temp_data = {}
                    temp_data['symbol'] = item['symbol']
                    temp_data['last_price'] = str(item['last_price'])
                    temp_data['short_min'] = str(item['short']['min'])
                    temp_data['short_max'] = str(item['short']['max'])
                    temp_data['short_price_percent'] = item['short']['price_percent']
                    temp_data['short_last'] = str(item['short']['last'])
                    temp_data['short_last_percent'] = item['short']['last_percent']
                    temp_data['long_min'] = str(item['long']['min'])
                    temp_data['long_max'] = str(item['long']['max'])
                    temp_data['long_price_percent'] = item['long']['price_percent']
                    temp_data['long_last'] = str(item['long']['last'])
                    temp_data['long_last_percent'] = item['long']['last_percent']
                    if operator == "and":
                        if (item['short']['last_percent'] >= short_min and item['short'][
                            'last_percent'] <= short_max) and (
                                item['long']['last_percent'] >= long_min and item['long']['last_percent'] <= long_max):
                            result.append(temp_data)
                    elif operator == "or":
                        if (item['short']['last_percent'] >= short_min and item['short'][
                            'last_percent'] <= short_max) or (
                                item['long']['last_percent'] >= long_min and item['long']['last_percent'] <= long_max):
                            result.append(temp_data)
                result_json = {"aaData": result}
                path = settings.TEMPLATES_ROOT + "/pages/user/html/api/security_" + str(security_id) + ".json"
                with open(path, 'w', encoding="utf-8") as f:
                    json.dump(result_json, f)
                context = {
                    "today": today_date,
                    "security": security,
                    "atr_data": data.atr_data,
                    "last_price": format(data.history_data['Close'].values[-1], '.2f'),
                }
                return HttpResponse(template.render(context, request))
            else:
                security = Security.objects.filter(id=id, user_id=user_id).values()[0]
                data = data_model(user_id, id)
                template = loader.get_template('pages/user/html/dashboard_view.html')
                context = {
                    "today": today_date,
                    "security": security,
                    "atr_data": data.atr_data,
                    "last_price": format(data.history_data['Close'].values[-1], '.2f'),
                }
                return HttpResponse(template.render(context, request))

        else:
            return redirect('login')
    except Exception as e:
        print(e)
        request.session.flush()
        template = loader.get_template('pages/landingpage/login.html')
        context = {'login_error': "You have no permission to connect this link."}
        return HttpResponse(template.render(context, request))

def admin_dashboard(request, id):
    try:
        permission = request.session['permission']
        user_id = request.session['user_id']
        today_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=6)).strftime("%Y-%m-%d")
        if request.session['permission'] == 1:
            if id == "all":
                template = loader.get_template('pages/user/html/admin_dashboard.html')
                stock_list, cfd_list, cfd_index_list, forex_list = get_symbol_list()
                temp_list = Security.objects.filter(user_id=user_id).values()
                security_list = []
                for security in temp_list:
                    rest_date = get_rest_trading_days(security['expire_date'])
                    symbol_count = len(security['symbols'].split(","))
                    if rest_date > 0 :
                        security['rest_days'] = rest_date
                    else:
                        security['rest_days'] = "Expired"
                    security['symbol_count'] = symbol_count
                    security_list.append(security)
                request.session['permission'] = 1
                request.session['user_id'] = request.session['user_id']
                context = {
                    "today": today_date,
                    "security_list": security_list,
                    "stock_list": stock_list,
                    "cfd_list": cfd_list,
                    "cfd_index_list": cfd_index_list,
                    "forex_list": forex_list
                }
                return HttpResponse(template.render(context, request))
            elif id == "filter":
                security_id = request.POST['security_id']
                security = Security.objects.filter(id=security_id, user_id=user_id).values()[0]
                data = data_model(user_id, security_id)
                template = loader.get_template('pages/user/html/admin_dashboard_view.html')
                short_min = request.POST['short_min']
                short_max = request.POST['short_max']
                long_min = request.POST['long_min']
                long_max = request.POST['long_max']
                operator = request.POST['operator']
                result = []
                atr_data = data.atr_data
                for item in atr_data:
                    temp_data = {}
                    temp_data['symbol'] = item['symbol']
                    temp_data['last_price'] = str(item['last_price'])
                    temp_data['short_min'] = str(item['short']['min'])
                    temp_data['short_max'] = str(item['short']['max'])
                    temp_data['short_price_percent'] = item['short']['price_percent']
                    temp_data['short_last'] = str(item['short']['last'])
                    temp_data['short_last_percent'] = item['short']['last_percent']
                    temp_data['long_min'] = str(item['long']['min'])
                    temp_data['long_max'] = str(item['long']['max'])
                    temp_data['long_price_percent'] = item['long']['price_percent']
                    temp_data['long_last'] = str(item['long']['last'])
                    temp_data['long_last_percent'] = item['long']['last_percent']
                    if operator == "and":
                        if (item['short']['last_percent'] >= short_min and item['short'][
                            'last_percent'] <= short_max) and (
                                item['long']['last_percent'] >= long_min and item['long']['last_percent'] <= long_max):
                            result.append(temp_data)
                    elif operator == "or":
                        if (item['short']['last_percent'] >= short_min and item['short'][
                            'last_percent'] <= short_max) or (
                                item['long']['last_percent'] >= long_min and item['long']['last_percent'] <= long_max):
                            result.append(temp_data)
                result_json = {"aaData": result}
                path = settings.MEDIA_ROOT + "/security/security_" + str(security_id) + ".json"

                with open(path, 'w', encoding="utf-8") as f:
                    json.dump(result_json, f)
                context = {
                    "today": today_date,
                    "security": security,
                    "atr_data": data.atr_data,
                    "last_price": format(data.history_data['Close'].values[-1], '.2f'),
                }
                return HttpResponse(template.render(context, request))
            else:
                security = Security.objects.filter(id=id, user_id=user_id).values()[0]
                '''
                hist_data = []
                bar_data = []
                sma_data = []
                ratio_data = []
                atr_data = []
                symbol_list = security['symbols'].split(",")
                rest_date = get_rest_trading_days(security['expire_date'])
                start_date = security['expire_date'] - datetime.timedelta(days=(int((rest_date + security['data_size']) / 5 + 10) * 7))
                for symbol in symbol_list:
                    temp_data = pdr.get_data_yahoo(symbol, start=start_date, end=datetime.datetime.today())
                    #del temp_data['Volume']
                    #del temp_data['Adj Close']
                    date_list = temp_data.index.tolist()
                    data_size = len(date_list)
                    if data_size > rest_date + security['data_size']:
                        temp_data = temp_data.iloc[data_size - rest_date - security['data_size']:]
                    #temp_dict = temp_data.to_dict()
                    if rest_date > 0:
                        data = {
                            "Open": list(tulipy.sma(temp_data['Open'].values, rest_date)),
                            "High": list(tulipy.sma(temp_data['High'].values, rest_date)),
                            "Low": list(tulipy.sma(temp_data['Low'].values, rest_date)),
                            "Close": list(tulipy.sma(temp_data['Close'].values, rest_date))
                        }
                    else:
                        data = {
                            "Open": list(temp_data['Open'].values),
                            "High": list(temp_data['High'].values),
                            "Low": list(temp_data['Low'].values),
                            "Close": list(temp_data['Close'].values)
                        }
                    bar_data.append({
                        "symbol": symbol,
                        "data": data
                    })
                    sma_data.append({
                        "symbol": symbol,
                        "data": data['Close']
                    })

                for i in range(len(sma_data)):
                    bbb = []
                    if i > 0:
                        for k in range(i):
                            bbb.append(0)
                    bbb.append(1.0)
                    for j in range(i+1, len(sma_data)):
                        aaa = np.corrcoef(sma_data[i]['data'], sma_data[j]['data'])
                        bbb.append(aaa[0][1])
                    ratio_data.append(bbb)

                for symbol_data in bar_data:
                    short_data = []
                    long_data = []
                    for i in range(len(sma_data[0]['data'])):
                        if i > 0:
                            short = max(symbol_data['data']['High'][i] - symbol_data['data']['Close'][i], abs(symbol_data['data']['High'][i] - symbol_data['data']['Close'][i-1]), abs(symbol_data['data']['Low'][i] - symbol_data['data']['Close'][i-1]))
                        else:
                            short = symbol_data['data']['High'][i] - symbol_data['data']['Low'][i]
                        long = abs(float(symbol_data['data']['Open'][i] - symbol_data['data']['Close'][i]))
                        short_data.append(short)
                        long_data.append(long)
                    atr_data.append({
                        "symbol": symbol_data['symbol'],
                        "data": {
                            "short": short_data,
                            "long": long_data
                        }
                    })



                    #ratio_data.append([np.corrcoef(sma_data[i]['data'], sma_data[i]['data']), ""]):
                '''
                data = data_model(user_id, id)
                template = loader.get_template('pages/user/html/admin_dashboard_view.html')
                write_to_json(data, security['id'])
                context = {
                    "today": today_date,
                    "security": security,
                    "atr_data": data.atr_data,
                    "last_price": format(data.history_data['Close'].values[-1], '.2f'),
                }
                return HttpResponse(template.render(context, request))
        else:
            request.session.flush()
            template = loader.get_template('pages/landingpage/login.html')
            context = {'login_error': "You have no permission to connect this link."}
            return HttpResponse(template.render(context, request))
    except Exception as e:
        print(e)
        request.session.flush()
        template = loader.get_template('pages/landingpage/login.html')
        context = {'login_error': "You have no permission to connect this link."}
        return HttpResponse(template.render(context, request))

def admin_user_setting(request):
    if request.session['permission'] == 1:
        user_list = Account.objects.all().values()
        template = loader.get_template('pages/user/html/admin_user_settings.html')
        today_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=6)).strftime("%Y-%m-%d")
        context = {
            "today": today_date,
            "user_list": user_list
        }
        return HttpResponse(template.render(context, request))
    else:
        request.session.flush()
        template = loader.get_template('pages/landingpage/login.html')
        context = {'login_error': "You have no permission to connect this link."}
        return HttpResponse(template.render(context, request))

def add_user(request):
    if request.method == "POST":
        if request.session['permission'] == 1:
            sure_name = request.POST['sure_name']
            user_id = request.POST['user_id']
            password = request.POST['password']
            status = request.POST['status']
            phone = request.POST['phone_number']
            expire = request.POST['expire_date']
            ib_name = request.POST['ib_user_name']
            ib_id = request.POST['ib_id']
            ib_port = request.POST['ib_port']
            saxo_token = request.POST['saxo_token']
            new_user = Account(sure_name=sure_name, user_id=user_id, password=password, status=status,
                                                 phone_number=phone, expire_date=expire, ib_user_name=ib_name,
                                                 ib_id=ib_id, ib_port=ib_port, saxo_token=saxo_token)
            new_user.save()
            messages.success(request, "Add new user successfully.")
            return redirect('admin_user_setting')
        else:
            request.session.flush()
            template = loader.get_template('pages/landingpage/login.html')
            context = {'login_error': "You have no permission to create new user."}
            return HttpResponse(template.render(context, request))

def get_user_info(request):
    if request.method == "POST":
        if request.session['permission'] == 1:
            id = request.POST['id']
            user = Account.objects.filter(id=id).values()[0]
            context = {
                "user": user
            }
            return JsonResponse(context)
        else:
            request.session.flush()
            template = loader.get_template('pages/landingpage/login.html')
            context = {'login_error': "You have no permission to connect this link."}
            return HttpResponse(template.render(context, request))

def update_user(request):
    if request.method == "POST":
        if request.session['permission'] == 1:
            id = request.POST['edit_id']
            sure_name = request.POST['edit_sure_name']
            user_id = request.POST['edit_user_id']
            password = request.POST['edit_password']
            status = request.POST['edit_status']
            phone = request.POST['edit_phone_number']
            expire = request.POST['edit_expire_date']
            ib_name = request.POST['edit_ib_user_name']
            ib_id = request.POST['edit_ib_id']
            ib_port = request.POST['edit_ib_port']
            saxo_token = request.POST['edit_saxo_token']
            Account.objects.filter(id=id).update(sure_name=sure_name, user_id=user_id, password=password, status=status, phone_number=phone, expire_date=expire, ib_user_name=ib_name, ib_id=ib_id, ib_port=ib_port, saxo_token=saxo_token)
            messages.success(request, "Update user information successfully.")
            return redirect('admin_user_setting')
        else:
            request.session.flush()
            template = loader.get_template('pages/landingpage/login.html')
            context = {'login_error': "You have no permission to connect this link."}
            return HttpResponse(template.render(context, request))

def add_security(request):
    if request.method == "POST" :
        try:
            permission = request.session['permission']
            print(permission)
            print()
            if permission > 0:
                name = request.POST['name']
                security_type = request.POST['type']
                expire = request.POST['expire']
                symbol = request.POST['symbol']
                data_size = request.POST['bar_size']
                new_security = Security(name=name, type=security_type, expire_date=expire, symbols=symbol, data_size=data_size)
                new_security.save()
                messages.success(request, "Add new security successfully.")
                context = {
                    "permission": permission
                }
                return JsonResponse(context)
            else:
                request.session.flush()
                template = loader.get_template('pages/landingpage/login.html')
                context = {'login_error': "You have no permission to connect this link."}
                return HttpResponse(template.render(context, request))

        except:
            request.session.flush()
            template = loader.get_template('pages/landingpage/login.html')
            context = {'login_error': "You have no permission to connect this link."}
            return HttpResponse(template.render(context, request))

def update_security(request):
    if request.method == "POST" :
        try:
            permission = request.session['permission']
            user_id = request.session['user_id']
            if permission > 0:
                id = request.POST['id']
                name = request.POST['name']
                security_type = request.POST['type']
                expire = request.POST['expire']
                symbol = request.POST['symbol']
                data_size = request.POST['bar_size']
                Security.objects.filter(id=id, user_id=user_id).update(name=name, type=security_type, expire_date=expire, symbols=symbol, data_size=data_size)
                messages.success(request, "Update security successfully.")
                context = {}
                return JsonResponse(context)
            else:
                request.session.flush()
                template = loader.get_template('pages/landingpage/login.html')
                context = {'login_error': "You have no permission to connect this link."}
                return HttpResponse(template.render(context, request))

        except:
            request.session.flush()
            template = loader.get_template('pages/landingpage/login.html')
            context = {'login_error': "You have no permission to connect this link."}
            return HttpResponse(template.render(context, request))

def get_security_info(request):
    if request.method == "POST":
        permission = request.session['permission']
        user_id = request.session['user_id']
        if permission > 0:
            id = request.POST['id']
            security_list = Security.objects.filter(user_id=user_id, id=id).values()
            if security_list == []:
                messages.warning(request, "There is a problem in your action. Please ask Administrator")
                context = {}
            else:
                security = security_list[0]
                symbol = security['symbols'].split(",")
                security['symbols'] = symbol
                context = {
                    "security": security
                }

            return  JsonResponse(context)
        else:
            request.session.flush()
            template = loader.get_template('pages/landingpage/login.html')
            context = {'login_error': "You have no permission to connect this link."}
            return HttpResponse(template.render(context, request))

def delete_security(request, id):
    try:
        user_permission = request.session['permission']
        request.session['permission'] = user_permission
        user_id = request.session['user_id']
        request.session['user_id'] = user_id
    except:
        return HttpResponseRedirect(reverse('login'))
    try:
        user_id = request.session['user_id']
        security_list = Security.objects.filter(user_id=user_id, id=id).values()
        permission = Account.objects.filter(id=user_id).values()[0]['permission']
        if security_list == []:
            messages.warning(request, "There is a problem in deleting security. Please ask Administrator")
        else:
            Security.objects.filter(id=id, user_id=user_id).delete()
            messages.success(request, "Delete security successfully.")

        if permission == 1:
            return redirect('admin_dashboard', id='all')
        else:
            return redirect('dashboard', id='all')
    except:
        request.session.flush()
        template = loader.get_template('pages/landingpage/login.html')
        context = {'login_error': "Now you are unauthorized user. Please login with your account."}
        return HttpResponse(template.render(context, request))

def percentile_filter(request):
    if request.method == "POST":
        security_id = request.POST['security_id']
        short_min = request.POST['short_min']
        short_max = request.POST['short_max']
        long_min = request.POST['long_min']
        long_max = request.POST['long_max']
        operator = request.POST['operator']
        user_id = request.session['user_id']
        data = data_model(user_id, security_id)
        print(operator)
        print(security_id)
        result = []
        atr_data = data.atr_data

        for item in atr_data:
            temp_data = {}
            temp_data['symbol'] = item['symbol']
            temp_data['last_price'] = str(item['last_price'])
            temp_data['short_min'] = str(item['short']['min'])
            temp_data['short_max'] = str(item['short']['max'])
            temp_data['short_price_percent'] = item['short']['price_percent']
            temp_data['short_last'] = str(item['short']['last'])
            temp_data['short_last_percent'] = item['short']['last_percent']
            temp_data['long_min'] = str(item['long']['min'])
            temp_data['long_max'] = str(item['long']['max'])
            temp_data['long_price_percent'] = item['long']['price_percent']
            temp_data['long_last'] = str(item['long']['last'])
            temp_data['long_last_percent'] = item['long']['last_percent']
            if operator == "and":
                if (item['short']['last_percent'] >= short_min and item['short']['last_percent'] <= short_max) and (item['long']['last_percent'] >= long_min and item['long']['last_percent'] <= long_max):
                    result.append(temp_data)
            elif operator == "or":
                if (item['short']['last_percent'] >= short_min and item['short']['last_percent'] <= short_max) or (item['long']['last_percent'] >= long_min and item['long']['last_percent'] <= long_max):
                    result.append(temp_data)

        print(result)
        result_json = {"aaData": result}
        path = settings.TEMPLATES_ROOT + "/pages/user/html/api/security_" + str(security_id) + ".json"
        with open(path, 'w', encoding="utf-8") as f:
            json.dump(result_json, f)

        context = {
            "result": "success"
        }
        return JsonResponse(context)

