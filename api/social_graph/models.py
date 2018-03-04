from django.db import models
from neomodel import (config, StructuredNode, StructuredRel, StringProperty, IntegerProperty,
    UniqueIdProperty, RelationshipTo, RelationshipFrom, Relationship)

# config.DATABASE_URL = 'bolt://localhost:7687'

class Country(StructuredNode):
    code = StringProperty(unique_index=True, required=True)

    # traverse incoming IS_FROM relation, inflate to Person objects
    inhabitant = RelationshipFrom('Person', 'IS_FROM')

class Person(StructuredNode):
    """Class for creating a Neo4j structured node Person
    
    Arguments:
        StructuredNode {StructuredNode} -- This is a Neo4j class
    """
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True)
    age = IntegerProperty(index=True, default=0)

    # traverse outgoing IS_FROM relations, inflate to Country objects
    country = RelationshipTo(Country, 'IS_FROM')
    friend = Relationship('Person', 'FRIEND')

    def __init__(self, *initial_data, **kwargs):
        """
        This is a function for initializing the structured node class with parameters

        Arguments:
            *initial_data {dict} -- A dictionary can be passed and its keys mapped to fields

        Keyword Arguments:
            kwargs {any} -- Set additional fields
        """
        super().__init__()
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])
            
    def __getitem__(self, item):
        return self.__dict__[item]
    
    def __setitem__(self, key, item):
        self.__dict__[key] = item
    
    def get_props(self):
        return self.__dict__.copy()
