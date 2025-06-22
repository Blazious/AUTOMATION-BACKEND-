from rest_framework import serializers
from .models import Invoice, InvoiceItem
from client.models import Client

class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ['id', 'description', 'quantity', 'unit', 'unit_price', 'amount']

class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'client', 'client_name', 'collection',
            'date_issued', 'due_date', 'subtotal', 'vat', 'wht', 'total_due',
            'status', 'created_by', 'created_at', 'updated_at',
            'terms', 'notes', 'items'
        ]
        read_only_fields = ['invoice_number', 'subtotal', 'vat', 'wht', 'total_due', 'created_at', 'updated_at']

    def create(self, validated_data):
        collection = validated_data.get('collection')
        invoice = Invoice.objects.create(**validated_data)

        if collection:
            invoice.copy_collection_items()
            invoice.calculate_totals()

        return invoice
   
    def update(self, instance, validated_data):
        # allow partial update and recalc totals if necessary
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        instance.calculate_totals()
        return instance
