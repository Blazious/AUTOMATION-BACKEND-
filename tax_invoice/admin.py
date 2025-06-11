from django.contrib import admin
from .models import TaxInvoice

@admin.register(TaxInvoice)
class TaxInvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'tax_invoice_number', 'date_issued', 'e_tims_date', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'date_issued', 'e_tims_date']
    search_fields = ['tax_invoice_number', 'invoice__invoice_number', 'invoice__client__name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('invoice', 'tax_invoice_number', 'date_issued', 'e_tims_date', 'status', 'uploaded_file')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
