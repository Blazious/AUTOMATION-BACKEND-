from django.db import models
from django.conf import settings
from invoice.models import Invoice  # assuming your Invoice model is in invoice app

class TaxInvoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE, related_name='tax_invoice')
    tax_invoice_number = models.CharField(max_length=50, blank=True, null=True, help_text="Number issued by eTIMS")
    e_tims_date = models.DateField(blank=True, null=True, help_text="Date when eTIMS was generated")
    date_issued = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    uploaded_file = models.FileField(upload_to='tax_invoices/', blank=True, null=True, help_text="Upload PDF of tax invoice")

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Tax Invoice {self.tax_invoice_number or 'N/A'} for {self.invoice.invoice_number}"
