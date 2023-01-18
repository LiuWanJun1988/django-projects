from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.urls import reverse
from django.core.files.storage import FileSystemStorage


import numpy as np
import json

# Create your views here.

def main(request):
    template = loader.get_template('pages/main.html')
    context = {}
    return HttpResponse(template.render(context, request))


