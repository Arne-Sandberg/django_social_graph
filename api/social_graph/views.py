from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
import json
from .models import Person
from django.core import serializers
from neomodel import db
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
PERSON_LABEL = 'Person'
PERSON_PARAMS = dict.fromkeys(['name', 'age'])

def query_node_with_id(id, node_class, node_label):
    node_label = node_label
    results, meta = db.cypher_query('MATCH ({}) WHERE ID({}) = {} RETURN {}'.format(node_label, node_label, id, node_label))
    return [node_class.inflate(row[0]) for row in results]

# GET, POST /persons/
@csrf_exempt
def persons(request):
    if request.method == 'GET':
        node_set = Person.nodes.all()
        resData = []
        for node in node_set:
            resData.append(node.get_props())
        resData = json.dumps(resData)
        return HttpResponse(resData, content_type='application/json')

    elif request.method == 'POST':
        params = PERSON_PARAMS

        reqBody = json.loads(request.body)
        # validate request body
        for field in reqBody:
            if field not in params:
                return HttpResponse(400)
            params[field] = reqBody[field]

        # if valid -> map to StructuredNode 
        node = Person(params).save()
        resData = json.dumps(node.get_props())
        return HttpResponse(resData, content_type='application/json')

    else:
        return HttpResponse(400)

# GET /persons/<int:id>
@csrf_exempt
def person_with_id(request, id):
    params = PERSON_PARAMS
    node_set = query_node_with_id(id, Person, PERSON_LABEL)
    node = node_set[0] if node_set else None

    if node:
        if request.method == 'GET':
            resData = json.dumps(node.get_props())
            return HttpResponse(resData, content_type='application/json')
        
        # PATCH
        if request.method == 'PATCH':
            reqBody = json.loads(request.body)
            for field in reqBody:
                if field not in params:
                    return HttpResponse(400)
                node[field] = reqBody[field]
            node.save()
            resData = json.dumps(node.get_props())
            return HttpResponse(resData, content_type='application/json')

        # DELETE: Protect with admin
        if request.method == 'DELETE':
            return HttpResponse(node.delete())

    else:
        # no data
        return HttpResponse()

    