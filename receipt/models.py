# receipt/models.py
from django.db import models
from django.conf import settings
from invoice.models import Invoice
from client.models import Client
from django.utils.timezone import now

class Receipt(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('mpesa', 'Mpesa'),
        ('bank', 'Bank Transfer'),
    ]

    receipt_number = models.CharField(max_length=20, unique=True, blank=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='receipts')
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    date_paid = models.DateField(default=now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.receipt_number or f"Receipt for {self.invoice.invoice_number}"

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = self.generate_receipt_number()
        super().save(*args, **kwargs)

    def generate_receipt_number(self):
        year = now().year
        prefix = f"RCPT-{year}"
        last_receipt = Receipt.objects.filter(receipt_number__startswith=prefix).order_by('receipt_number').last()
        if last_receipt:
            last_number = int(last_receipt.receipt_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        return f"{prefix}-{new_number:03d}"