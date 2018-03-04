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

def query_node_with_uid(uid, node_class):
    return node_class.nodes.get(uid=uid)

def delete_node(node):
    return node.delete()

@csrf_exempt
def create_relationship(request):
    if request.method == 'POST':
        reqBody = json.loads(request.body)
        from_node_with_id = reqBody['from']
        to_node_with_id = reqBody['to']

        from_node = query_node_with_uid(from_node_with_id, Person)
        print(from_node)
        to_node = query_node_with_uid(to_node_with_id, Person)
        print(to_node)

        return HttpResponse(from_node.friend.connect(to_node))

    return HttpResponse('GET method not allowed.')

# GET, POST /persons/
@csrf_exempt
def persons(request):
    if request.method == 'GET':
        node_set = Person.nodes.all()
        resData = []
        for node in node_set:
            resData.append(node.get_props())
        print(resData[0])
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
            return delete_node(node)

    else:
        # no data
        return HttpResponse()

    