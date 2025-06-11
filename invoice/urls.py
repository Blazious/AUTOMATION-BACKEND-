from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvoiceViewSet, invoice_pdf_view 

router = DefaultRouter()
router.register(r'invoices', InvoiceViewSet, basename='invoice')

urlpatterns = [
    path('', include(router.urls)),
    path('invoices/<int:pk>/pdf/', invoice_pdf_view, name='invoice-pdf'),
]
