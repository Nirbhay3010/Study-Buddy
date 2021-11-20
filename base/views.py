from django.shortcuts import render
from django.http.response import HttpResponse
# Create your views here.
from .models import Room
from .forms import RoomForm
# rooms=[
#     {'id':1,'name':'Go Python!!'},
#     {'id':2,'name':'Go DSA!!'},
#     {'id':3,'name':'Go Js!!'},
# ]

def home(request):
    rooms=Room.objects.all()
    context={'rooms':rooms}
    return render(request,'base/home.html',context)

def room(request,pk):
    room=Room.objects.get(id=pk)
    context={'room':room}
    return render(request,'base/room.html',context)

def createRoom(request):
    form = RoomForm()
    if request.method =='POST':
        print(requst.POST)
    context= {'form':form}
    return render(request,'base/room_form.html',context)