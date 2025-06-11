from django.contrib import admin
from .models import Invoice, InvoiceItem

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    readonly_fields = ('amount',)  # amount auto-calculated

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'client', 'date_issued', 'due_date', 'total_due', 'status', 'created_by']
    list_filter = ['status', 'date_issued', 'due_date']
    search_fields = ['invoice_number', 'client__name']
    date_hierarchy = 'date_issued'
    inlines = [InvoiceItemInline]
    readonly_fields = ['subtotal', 'vat', 'wht', 'total_due']
    ordering = ['-date_issued']

@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'description', 'quantity', 'unit', 'unit_price', 'amount']
    search_fields = ['invoice__invoice_number', 'description']
