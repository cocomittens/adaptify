from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['POST'])
def login(request):
    pass

@api_view(['POST'])
def signup(request):
    pass