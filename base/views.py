from django.shortcuts import render
from django.http.response import HttpResponse
# Create your views here.

rooms=[
    {'id':1,'name':'Go Python!!'},
    {'id':2,'name':'Go DSA!!'},
    {'id':3,'name':'Go Js!!'},
]

def home(request):
    return render(request,'base/home.html',{'rooms':rooms})

def room(request,pk):
    room=None
    for i in rooms:
        if i['id']==int(pk):
            room = i
    context={'room':room}
    return render(request,'base/room.html',context)
