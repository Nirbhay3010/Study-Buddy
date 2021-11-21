from django.shortcuts import render, redirect
from django.db.models import Q
from django.http.response import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Room,Topic
from .forms import RoomForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('homepage')

    if request.method=='POST':
        uname= request.POST.get('username').lower()
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

def home(request):
    query = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms=Room.objects.filter(
        Q(topic__name__icontains=query) |
        Q(name__icontains=query) |
        Q(description__icontains=query)
        )
    topics = Topic.objects.all()
    room_count = rooms.count()
    context={'rooms':rooms, 'topics': topics, 'room_count':room_count}
    return render(request,'base/home.html',context)

def room(request,pk):
    room=Room.objects.get(id=pk)
    context={'room':room}
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



