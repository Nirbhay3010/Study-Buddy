from django.shortcuts import render, redirect
from django.db.models import Q
from django.http.response import HttpResponse,HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Message,Room,Topic,User
from .forms import RoomForm,UserForm,MyUserCreationForm
from django.contrib.auth import authenticate,login,logout


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
    form=MyUserCreationForm()

    if request.method=="POST":
        form = MyUserCreationForm(request.POST)
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
    context = {'user':user,'rooms':user_rooms,'topics':topics,'room_messages':room_messages}
    return render(request, 'base/user_profile.html',context)

def home(request):
    query = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms=Room.objects.filter(
        Q(topic__name__icontains=query) |
        Q(name__icontains=query) |
        Q(description__icontains=query)
        )
    topics = Topic.objects.all()[0:5]
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=query))
    context={'rooms':rooms, 'topics': topics, 'room_messages':room_messages}
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
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name=request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        
        return redirect('homepage')
    context= {'form':form,'topics':topics}
    return render(request,'base/room_form.html',context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse("You are not allowed to update the room that you did not create")

    

    if request.method =='POST':
        topic_name=request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        form = RoomForm(request.POST, instance=room)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('homepage')

    context={'form':form,'room':room}
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

@login_required(login_url='login')
def updateUser(request):
    user=request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST,request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk=user.id)
    context = {'form':form}
    
    return render(request,'base/update-user.html',context)

def topicsPage(request):
    query = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=query)
    context={'topics':topics}
    return render(request,'base/topics.html',context)

def activityPage(request):
    room_messages=Message.objects.all()[0:2]
    context={'room_messages':room_messages}
    return render(request,'base/activity.html',context)