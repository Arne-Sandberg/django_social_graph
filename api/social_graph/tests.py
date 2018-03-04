from django.test import TestCase, Client
from neomodel import db
from .models import Person
from . import views
from django.http import HttpRequest, HttpResponse
import json

# Create your tests here.
class PersonsTestCase(TestCase):
    def setUp(self):
        self.a = Person(name='test_a').save()
        self.b = Person(name='test_b', age=23).save()
        self.c = Person(name='test_c', age=1000).save()
        self.client = Client()
    
    def tearDown(self):
        views.delete_node(self.a)
        views.delete_node(self.b)
        views.delete_node(self.c)

    def test_query_node_with_uid(self):
        node = views.query_node_with_uid(self.a.uid, Person)
        self.assertEqual(node, self.a)
        self.assertNotEqual(node, self.b)

    def test_post_req_is_valid(self):
        params = dict.fromkeys(['string', 'int', 'bool'])
        req_body = {
            "string": "Test_A",
            "int": 23,
            "bool": True
        }
        
        # param keys should be equal to req_body keys
        self.assertEqual(views.post_req_is_valid(req_body, params), True)

        # partial req body should be rejected
        partial_req_body = req_body.copy()
        partial_req_body.pop('bool', None)
        self.assertEqual(views.post_req_is_valid(partial_req_body, params), False)

        # invalid req_body key should be rejected
        invalid_req_body = req_body.copy()
        invalid_req_body['invalid'] = invalid_req_body.pop('bool')
        self.assertEqual(views.post_req_is_valid(invalid_req_body, params), False)

    def test_patch_req_is_valid(self):
        params = dict.fromkeys(['string', 'int', 'bool'])
        req_body = {
            "string": "Test_A",
            "int": 23,
            "bool": True
        }

        # complete req_body should evaluate to True
        self.assertEqual(views.patch_req_is_valid(req_body, params), True)

        # partial req_body should evaluate to True
        partial_req_body = req_body.copy()
        partial_req_body.pop('bool', None)
        self.assertEqual(views.patch_req_is_valid(partial_req_body, params), True)

        # invalid req_body key should be rejected
        invalid_req_body = req_body.copy()
        invalid_req_body['invalid'] = 'key'
        self.assertEqual(views.patch_req_is_valid(invalid_req_body, params), False)

    def test_create_relationship(self):
        req_body = {
            "rel": "FRIEND",
            "from": self.a.uid,
            "to": self.b.uid
        }
        res = self.client.post('/api/create_rel', json.dumps(req_body), content_type='application/json')

        # should return HttpResponse
        self.assertIsInstance(res, HttpResponse)

        # Nodes A and B should be connected
        self.a.friend.is_connected(self.b)

    def test_get_persons(self):
        res = self.client.get('/api/persons')
        
        # should return HttpResponse
        self.assertIsInstance(res, HttpResponse)

        # should return node_set with length > 0
        node_set = res.content
        self.assertGreater(len(node_set), 0)

    def test_get_person_with_uid(self):
        res = self.client.get('/api/persons/{}'.format(self.a.uid))

        # should return HttpResponse
        self.assertIsInstance(res, HttpResponse)

        # should return JSON object with fields matching node with same uid
        res_content = json.loads(res.content.decode('utf-8'))
        for field in res_content:
            self.assertEqual(res_content[field], self.a[field])

