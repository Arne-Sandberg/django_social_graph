from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
import json
from .models import Person
from django.core import serializers
from neomodel import db
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
CREATE_RELATIONSHIP_PARAMS = dict.fromkeys(['rel', 'from', 'to'])
PERSON_PARAMS = dict.fromkeys(['name', 'age'])

# should return RelationshipDefinition
def find_rel(from_node, rel):
    if rel == 'FRIEND':
        return from_node.friend
    else:
        return None

def query_node_with_id(id, node_class, node_label):
    node_label = node_label
    results, meta = db.cypher_query('MATCH ({}) WHERE ID({}) = {} RETURN {}'.format(node_label, node_label, id, node_label))
    return [node_class.inflate(row[0]) for row in results]

def query_node_with_uid(uid, node_class):
    return node_class.nodes.get_or_none(uid=uid)

def delete_node(node):
    return node.delete()

def post_req_is_valid(req_body, params):
    is_valid = True
    if not req_body:
        is_valid = False
    if not all (param in params for param in req_body):
        is_valid = False
    if not all (field in req_body for field in params):
        is_valid = False
    return is_valid

def patch_req_is_valid(req_body, params):
    is_valid = True
    if not req_body:
        is_valid = False
    for field in req_body:
        if field not in params:
            is_valid = False
    return is_valid

# POST /create_rel
@csrf_exempt
def create_relationship(request):
    if request.method == 'POST':
        params = CREATE_RELATIONSHIP_PARAMS
        req_body = json.loads(request.body)
        if post_req_is_valid(req_body, params):
            from_node = query_node_with_uid(req_body['from'], Person)
            to_node = query_node_with_uid(req_body['to'], Person)
            # validate nodes
            if not from_node or not to_node:
                return HttpResponseBadRequest()

            relationship = find_rel(from_node, req_body['rel'])

            # validate relationship
            if not relationship:
                return HttpResponseBadRequest()

            relationship.connect(to_node)

            return HttpResponse(200)

        else:
            return HttpResponseBadRequest()

    return HttpResponseBadRequest()

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

        req_body = json.loads(request.body)
        # validate request body
        if post_req_is_valid(req_body, params):
            for field in req_body:
                params[field] = req_body[field]
            # if valid -> map to StructuredNode 
            node = Person(params).save()
            resData = json.dumps(node.get_props())
            return HttpResponse(resData, content_type='application/json')
        else:
            return HttpResponseBadRequest()

    else:
        return HttpResponseBadRequest()

# GET /persons/<int:id>
@csrf_exempt
def person_with_uid(request, uid):
    params = PERSON_PARAMS
    # node_set = query_node_with_id(id, Person, PERSON_LABEL)
    # node = node_set[0] if node_set else None
    node = query_node_with_uid(uid, Person)

    if node:
        if request.method == 'GET':
            resData = json.dumps(node.get_props())
            return HttpResponse(resData, content_type='application/json')
        
        # PATCH
        elif request.method == 'PATCH':
            req_body = json.loads(request.body)
            if patch_req_is_valid(req_body, params):
                for field in req_body:
                    node[field] = req_body[field]
                node.save()
                resData = json.dumps(node.get_props())
                return HttpResponse(resData, content_type='application/json')
            else:
                return HttpResponseBadRequest()

        # DELETE: Protect with admin
        elif request.method == 'DELETE':
            return delete_node(node)

        else:
            return HttpResponseBadRequest()

    else:
        # no data
        return HttpResponseBadRequest()

    