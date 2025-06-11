from django.db import models
from django.conf import settings
from client.models import Client
from collection_service.models import Collection, CollectionItem
from django.utils.timezone import now
from decimal import Decimal

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    invoice_number = models.CharField(max_length=20, unique=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    collection = models.ForeignKey(Collection, on_delete=models.SET_NULL, null=True, blank=True, help_text="Linked Collection")
    date_issued = models.DateField(default=now)
    due_date = models.DateField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    vat = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    wht = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    terms = models.TextField(default="Payment due within 30 days")
    notes = models.TextField(blank=True, default="Thank you for your business!")

    def __str__(self):
        return self.invoice_number or "Invoice (unsaved)"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        super().save(*args, **kwargs)
        # After saving invoice, if collection is linked and no items yet, copy collection items
        if self.collection and not self.items.exists():
            self.copy_collection_items()
            self.calculate_totals()

    def generate_invoice_number(self):
        year = now().year
        prefix = f"INV-{year}"
        last_invoice = Invoice.objects.filter(invoice_number__startswith=prefix).order_by('invoice_number').last()
        if last_invoice:
            last_number = int(last_invoice.invoice_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        return f"{prefix}-{new_number:03d}"

    def copy_collection_items(self):
        # copy each CollectionItem as an InvoiceItem
        collection_items = CollectionItem.objects.filter(collection=self.collection)
        invoice_items = []
        for item in collection_items:
            invoice_items.append(InvoiceItem(
                invoice=self,
                description=item.get_waste_category_display(),
                quantity=item.quantity,
                unit=item.unit,
                unit_price=item.unit_price,
                amount=item.quantity * item.unit_price,
            ))
        InvoiceItem.objects.bulk_create(invoice_items)

    def calculate_totals(self):
        self.subtotal = sum(item.amount for item in self.items.all())
        self.vat = self.subtotal *  Decimal('0.16') # 16% VAT
        self.wht = self.subtotal *  Decimal('0.02') # 2% WHT
        self.total_due = self.subtotal + self.vat - self.wht
        super().save(update_fields=['subtotal', 'vat', 'wht', 'total_due'])


    @property
    def total_paid(self):
        from receipt.models import Receipt  # import here to avoid circular import
        return sum(receipt.amount for receipt in self.receipts.all())

    @property
    def balance_due(self):
        return max(Decimal('0.00'), self.total_due - self.total_paid)
 
    @property
    def is_fully_paid(self):
        return self.balance_due <= Decimal('0.00')


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True)

    def save(self, *args, **kwargs):
        self.amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} - {self.amount}"
