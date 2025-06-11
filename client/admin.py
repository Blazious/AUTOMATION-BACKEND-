from django.contrib import admin

# Register your models here.
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'phone', 'email', 'wht_agent']
    search_fields = ['name', 'city', 'email']
    list_filter = ['wht_agent', 'city']