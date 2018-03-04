from django.conf.urls import url, include
from django.urls import path
from . import views

urlpatterns = [
    path(r'persons', views.persons),   
    path(r'persons/<str:uid>', views.person_with_uid),
    path(r'create_rel', views.create_relationship) 
]