from django.test import TestCase
from neomodel import db
from .models import Person
from . import views
from django.http import HttpRequest, HttpResponse

# Create your tests here.
class PersonsTestCase(TestCase):
    def setUp(self):
        self.a = Person(name='test_a').save()
        self.b = Person(name='test_b', age=23).save()
        self.c = Person(name='test_c', age=1000).save()
    
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

    def test_get_persons(self):
        req = HttpRequest()
        req.method = 'GET'
        res = views.persons(req)
        
        # should return HttpResponse
        self.assertIsInstance(res, HttpResponse)

        # should return node_set with length > 0
        node_set = res.content
        self.assertGreater(len(node_set), 0)

