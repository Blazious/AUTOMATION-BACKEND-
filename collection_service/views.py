from rest_framework import viewsets, permissions
from .models import Collection, CollectionItem
from expenses.models import Expense,GeneralExpense
from .serializers import CollectionSerializer, CollectionItemSerializer, ExpenseSerializer, GeneralExpenseSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all().order_by('-date_collected')
    serializer_class = CollectionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class CollectionItemViewSet(viewsets.ModelViewSet):
    queryset = CollectionItem.objects.all()
    serializer_class = CollectionItemSerializer
    permission_classes = [IsAuthenticated]

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

class GeneralExpenseViewSet(viewsets.ModelViewSet):
    queryset = GeneralExpense.objects.all()
    serializer_class = GeneralExpenseSerializer
    permission_classes = [IsAuthenticated]

