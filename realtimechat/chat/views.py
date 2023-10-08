from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required
from account.models import User
from .models import Room
from django.contrib import messages
from account.forms import AddUserForm, EditUserForm
from django.contrib.auth.models import Group
# Create your views here.

@login_required
def admin(request):
    if request.user.is_staff:
        rooms = Room.objects.all()
        users = User.objects.all()
        return render(request, 'chat/admin.html', {
            'rooms':rooms,
            'users':users
        })
    else:
        return JsonResponse({'Message':'error'})


def create_room(request, uuid):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        url = request.POST.get('url', '')

        Room.objects.create(uuid=uuid, client=name, url=url)

        return JsonResponse({'Message':'Room Created'})

@login_required
def room(request, uuid):
    room = Room.objects.get(uuid=uuid)

    if room.status == Room.WAITING:
        room.status = Room.ACTIVE
        room.agent = request.user
        room.save()
    elif room.status == Room.ACTIVE:
        room.agent = request.user
        room.save()

    return render(request, 'chat/room.html', {
        'room':room
    })
    
@login_required
def add_user(request):
    
    if request.user.has_perm('user.add_user'):
        if request.method == 'POST':
            form = AddUserForm(request.POST)
            
            if form.is_valid():
                user = form.save(commit=False)
                user.is_staff = True
                user.set_password(request.POST.get('password'))
                user.save()

                if user.role == User.MANAGER:
                    group = Group.objects.get(name= 'Managers')
                    group.user_set.add(user)

                messages.success(request, 'The user was added!')

                return redirect ('/chat-admin/')


        else:
            form = AddUserForm()
        return render(request, 'chat/add_user.html', {'form': form})
    else:
        messages.error(request, 'You dont have permission to add a user')
        return redirect('/chat-admin/')


@login_required
def user_detail(request, uuid):
    user = User.objects.get(pk =uuid)
    rooms = user.rooms.all()

    return render(request, 'chat/user_detail.html', {'user':user, 'rooms':rooms})

@login_required
def edit_user(request, uuid):
    if request.user.has_perm('user.edit_user'):
        user = User.objects.get(pk = uuid)
        if request.method == 'POST':
            form = EditUserForm(request.POST, instance=user)
            if form.is_valid():
                form.save()

                messages.success(request, 'Changes made were saved')

                return redirect('/chat-admin/')
        else:
            form = EditUserForm(instance=user)

        return render(request, 'chat/edit_user.html', {'form':form, 'user':user})
    else:
        messages.error(request, 'You dont have permission to edit a user')
        return redirect('/chat-admin/')

@login_required
def delete_room(request, uuid):
    if request.user.has_perm('room.delete_room'):
        room = Room.objects.get(uuid=uuid)
        room.delete()
        messages.error(request, 'Deleted successfully')
        return redirect('/chat-admin/')

    else:
        messages.error(request, 'You dont have permission to edit a user')
        return redirect('/chat-admin/')
