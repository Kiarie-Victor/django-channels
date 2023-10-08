from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace='core')),
    path('', include('chat.urls', namespace='chat')),
    path('', include('account.urls')),
    
]