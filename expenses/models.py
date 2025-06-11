from django.db import models
from collection_service.models import Collection

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('fuel', 'Fuel'),
        ('truck_hire', 'Truck Hire'),
        ('casuals', 'Casuals'),
        ('dumping_fee', 'Dumping Fee'),
        ('ppe', 'PPE'),
        ('other', 'Other'),
    ]

    collection = models.ForeignKey(Collection,on_delete=models.SET_NULL,null=True,blank=True,related_name='expenses')
    date = models.DateField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=255, blank=True, null=True)
    receipt = models.FileField(upload_to='receipts/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date} - {self.get_category_display()} - {self.amount}"
    
class GeneralExpense(models.Model):
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    receipt = models.FileField(upload_to='general_expense_receipts/', null=True, blank=True)

    def __str__(self):
        return f"{self.description} - {self.amount}"    
