from django.conf.urls import url, include
from django.urls import path
from . import views

urlpatterns = [
    path(r'persons', views.persons),   
    path(r'persons/<int:id>', views.person_with_id)     
]