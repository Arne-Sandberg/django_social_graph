from django.shortcuts import render
from django.http import HttpResponse
import json
from .models import Person
from django.core import serializers

# Create your views here.
def get_persons(request):
    query = Person.nodes.get(name='Colin')
    resData = json.dumps(query.__properties__)
    return HttpResponse(resData, content_type='application/json')