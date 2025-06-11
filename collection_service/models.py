from django.db import models
from django.conf import settings
from client.models import Client  # Assuming Client model is in client app



# Create your models here.

class Collection(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='collections')
    date_collected = models.DateField()
    due_date = models.DateField()
    invoiced = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,  related_name='collections_created')

    def __str__(self):
        return f"{self.client.name} - {self.date_collected}"

class CollectionItem(models.Model):
    WASTE_CATEGORY_CHOICES = [
        # Premium Tier
        ('biohazard', 'Biohazard Collection (Hospitals)'),
        ('chemical', 'Chemical Waste Disposal (Labs)'),
        ('pharmaceutical', 'Pharmaceutical Waste (Expired Meds)'),
        ('sharps', 'Sharps Pickup & Disposal'),

        # Industrial Tier
        ('grain_byproducts', 'Grain Industry Byproducts'),
        ('scrap_packaging', 'Scrap & Packaging Waste'),
        ('processing_sludge', 'Processing Sludge'),
        ('scheduled_bulk', 'Scheduled Bulk Pickups'),

        # Residential & SME Tier
        ('household_mixed', 'Household Mixed Waste Collection'),
        ('recyclables', 'Recyclables Pickup (Plastics/Papers)'),
        ('food_organic', 'Food & Organic Waste'),
        ('estate_flats', 'Estate/Flats Scheduled Service'),

        # Eco & Circular Tier
        ('ewaste', 'E-Waste Collection (phones, laptops)'),
        ('compostable', 'Compostable Waste for Farms'),
        ('glass_plastic', 'Glass & Plastic Pickup'),
        ('office_recycling', 'Office Recycling Programs'),
    ]

    # Unit Choices from tiers summary
    UNIT_CHOICES = [
        ('kg', 'Kilogram (kg)'),
        ('litre', 'Litre'),
        ('container', 'Container'),
        ('trip', 'Trip'),
        ('ton', 'Ton'),
        ('bin', 'Bin'),
        ('month', 'Month'),
        ('service_session', 'Service Session'),
        ('bag', 'Bag'),
    ]




    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='items')
    waste_category = models.CharField(max_length=100,choices=WASTE_CATEGORY_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20,choices=UNIT_CHOICES)  # e.g., kg, mo (month)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        # auto calculate amount if not provided
        self.amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_waste_category_display()} - {self.quantity} {self.unit}"