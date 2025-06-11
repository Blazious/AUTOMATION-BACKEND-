from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReceiptViewSet, receipt_pdf_view

router = DefaultRouter()
router.register(r'receipts', ReceiptViewSet, basename='receipt')

urlpatterns = [
    path('', include(router.urls)),
    path('receipts/<int:receipt_id>/pdf/', receipt_pdf_view, name='receipt-pdf'),
]

