# analytics/serializers.py
from rest_framework import serializers

class FinancialSummarySerializer(serializers.Serializer):
    total_revenue = serializers.CharField()
    total_expenses = serializers.CharField()
    net_profit = serializers.CharField()
    net_profit_margin_percent = serializers.CharField()
    start_date = serializers.CharField(allow_null=True)
    end_date = serializers.CharField(allow_null=True)
    ai_summary = serializers.CharField(allow_blank=True, required=False)