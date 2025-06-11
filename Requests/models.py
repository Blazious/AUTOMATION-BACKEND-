from django.db import models
from client.models import Client 

class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('responded', 'Responded'),
        ('closed', 'Closed'),
    ]
    



    client = models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL)
    from_client = models.CharField(max_length=255)  # e.g., "Green Co."
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    date_received = models.DateTimeField(auto_now_add=True)
    preferred_collection_date = models.DateField(null=True, blank=True)
    frequency = models.CharField(max_length=100, blank=True)  # e.g., "One-time", "Weekly"
    additional_notes = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    is_collection_created = models.BooleanField(default=False)  # Mark if converted to a collection

    def __str__(self):
        return f"{self.from_client} - {self.subject} ({self.get_status_display()})"

     


    def save(self, *args, **kwargs):
        if not self.client and self.from_client:
            # Try to find existing client by name
            client, created = Client.objects.get_or_create(name=self.from_client)
            self.client = client
        super().save(*args, **kwargs) 