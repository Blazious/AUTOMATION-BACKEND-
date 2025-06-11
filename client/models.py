from django.db import models

# Create your models here.
class Client(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    wht_agent = models.BooleanField(default=False, help_text="Withholding Tax Agent")
    kra_pin = models.CharField(max_length=20, blank=True, null=True, help_text="Client's KRA PIN")

    def __str__(self):
        return self.name