# networking/admin.py

from django.contrib import admin
from .models import NetworkingConnection

@admin.register(NetworkingConnection)
class NetworkingConnectionAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('from_user__first_name', 'to_user__first_name')
    readonly_fields = ('created_at', 'updated_at')
