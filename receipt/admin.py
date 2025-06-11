from django.contrib import admin
from .models import Receipt

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = [
        'receipt_number', 
        'invoice', 
        'client', 
        'date_paid', 
        'amount', 
        'payment_method', 
        'created_by',
        'created_at'
    ]
    list_filter = ['payment_method', 'date_paid', 'client']
    search_fields = ['receipt_number', 'invoice__invoice_number', 'client__name']
    ordering = ['-date_paid']
