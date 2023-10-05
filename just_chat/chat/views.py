from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.safestring import mark_safe
import json

def index(request):
    return render(request, 'chat/index.html', {})

@login_required
def room(request, room_name):
    print(room_name)
    return render(request, 'chat/room.html', {
        'room_name': room_name
    })