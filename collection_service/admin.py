from django.contrib import admin

# Register your models here.
from .models import Collection, CollectionItem

class CollectionItemInline(admin.TabularInline):
    model = CollectionItem
    extra = 1

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['client', 'date_collected', 'due_date', 'invoiced', 'created_by']
    inlines = [CollectionItemInline]

@admin.register(CollectionItem)
class CollectionItemAdmin(admin.ModelAdmin):
    list_display = ['collection', 'waste_category', 'quantity', 'unit', 'unit_price', 'amount']
