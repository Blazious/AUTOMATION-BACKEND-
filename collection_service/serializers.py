from rest_framework import serializers
from .models import Collection, CollectionItem
from expenses.models import Expense, GeneralExpense
from client.serializers import ClientSerializer  # For nested display if needed

class CollectionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionItem
        fields = '__all__'
        read_only_fields = ['amount']  # auto-calculated on save

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'

class GeneralExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralExpense
        fields = '__all__'

class CollectionSerializer(serializers.ModelSerializer):
    items = CollectionItemSerializer(many=True )
    expenses = ExpenseSerializer(many=True, read_only=True)
    client = serializers.PrimaryKeyRelatedField(queryset=ClientSerializer.Meta.model.objects.all())

    class Meta:
        model = Collection
        fields = ['id', 'client', 'date_collected', 'due_date', 'invoiced', 'created_by', 'items', 'expenses']
        read_only_fields = ['created_by', 'expenses']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        collection = Collection.objects.create(**validated_data)

        for item_data in items_data:
            CollectionItem.objects.create(collection=collection, **item_data)

        return collection