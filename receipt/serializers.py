from rest_framework import serializers
from .models import Receipt

class ReceiptSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    balance_due = serializers.DecimalField(source='invoice.balance_due', read_only=True, max_digits=12, decimal_places=2)
    is_fully_paid = serializers.BooleanField(source='invoice.is_fully_paid', read_only=True)

    class Meta:
        model = Receipt
        fields = [
            'id', 'receipt_number', 'invoice', 'invoice_number', 'client', 'client_name',
            'amount', 'payment_method', 'date_paid',
            'created_by', 'created_at', 'balance_due', 'is_fully_paid'
        ]
        read_only_fields = ['receipt_number', 'created_by', 'created_at']
