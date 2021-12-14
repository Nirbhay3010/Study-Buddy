from django.shortcuts import render, redirect
from django.db.models import Q
from django.http.response import HttpResponse,HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Message, Room,Topic,Message
from .forms import RoomForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm

#login Page
def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('homepage')

    if request.method=='POST':
        uname= request.POST.get('username')
        pwd=request.POST.get('password')
        
        try:
            user = User.objects.get(username=uname)
        except:
            messages.error(request, "User Doesn't Exist")

        user = authenticate(request, username=uname,password=pwd)
        
        if user is not None:
            login(request, user)
            return redirect('homepage')
        else:
            messages.error(request,"Username or password doesn't exist")

    context={'page':page}
    return render(request, 'base/login_register.html',context)

#redirect after logout page
def logoutUser(request):
    logout(request)
    return redirect('homepage')


def registerPage(request):
    form=UserCreationForm()

    if request.method=="POST":
        form =UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect("homepage")
        else:
            messages.error(request,"Some Error occurred.")

    context={'form':form}
    return render(request,'base/login_register.html',context)

def userProfile(request,pk):
    user = User.objects.get(id=pk)
    user_rooms= user.room_set.all()
    room_messages=user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user,'user_rooms':user_rooms,'topics':topics,'room_messages':room_messages}
    return render(request, 'base/user_profile.html',context)

def home(request):
    query = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms=Room.objects.filter(
        Q(topic__name__icontains=query) |
        Q(name__icontains=query) |
        Q(description__icontains=query)
        )
    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=query))


    context={'rooms':rooms, 'topics': topics, 'room_count':room_count, 'room_messages':room_messages}
    return render(request,'base/home.html',context)


def room(request,pk):
    room=Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method=="POST":
        message = Message.objects.create(
            user = request.user,
            room = room,
            body=request.POST.get('message_sent')
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)

    context={'room':room, 'room_messages':room_messages,'participants':participants}
    return render(request,'base/room.html',context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    if request.method =='POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('homepage')
    context= {'form':form}
    return render(request,'base/room_form.html',context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse("You are not allowed to update the room that you did not create")

    if request.method =='POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('homepage')

    context={'form':form}
    return render(request, 'base/room_form.html',context)


@login_required(login_url='login')
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("You are not allowed to delete the room that you did not create")
    
    if request.method=="POST":
        room.delete()
        return redirect('homepage')
    return render(request,'base/delete.html',{'obj':room})


@login_required(login_url='login')
def deleteMessage(request,pk):
    message = Message.objects.get(id=pk)
    
    if request.user != message.user:
        return HttpResponse("You are only allowed to delete your own messages")
    
    if request.method == "POST":
        message.delete()
       
        return redirect('room',pk=message.room.id)
    return render(request,'base/delete.html',{'obj':message})



