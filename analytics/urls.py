# analytics/urls.py
from django.urls import path
from .views import FinancialSummaryAPIView, FinancialGraphAPIView

urlpatterns = [
    path('financial-summary/', FinancialSummaryAPIView.as_view(), name='financial-summary'),
    path('summary/graph/', FinancialGraphAPIView.as_view(), name='financial-graph'),
]
