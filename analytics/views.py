from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime, timedelta
from .services.summary import get_financial_summary
from .serializers import FinancialSummarySerializer
from transformers import pipeline
import io
import base64
import matplotlib.pyplot as plt
from django.http import JsonResponse
from django.views import View
from django.utils.timezone import now, timedelta
from invoice.models import Invoice
from expenses.models import Expense, GeneralExpense
from django.db.models import Sum
from collections import defaultdict
from .utils import generate_financial_line_chart



# Load the local text generation pipeline once
summarizer = pipeline("text-generation", model="distilgpt2")

class FinancialSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        period = request.query_params.get("period", "month")
        value = request.query_params.get("value")

        today = datetime.today().date()

        if period == "month" and value:
            year, month = map(int, value.split("-"))
            start = datetime(year, month, 1).date()
            if month == 12:
                end = datetime(year + 1, 1, 1).date() - timedelta(days=1)
            else:
                end = datetime(year, month + 1, 1).date() - timedelta(days=1)
        else:
            start = today.replace(day=1)
            end = today

        summary = get_financial_summary(start, end)

        # Generate summary with Transformers
        ai_summary = self.generate_ai_summary(summary)
        summary['ai_summary'] = ai_summary

        serializer = FinancialSummarySerializer(summary)
        return Response(serializer.data)

    def generate_ai_summary(self, summary_data):
        try:
            text_to_summarize = (
                f"Between {summary_data['start_date']} and {summary_data['end_date']}, the business generated a revenue of "
                f"{summary_data['total_revenue']} Kenyan Shillings. During this period, total expenses were recorded at "
                f"{summary_data['total_expenses']} Kenyan Shillings, resulting in a net profit of "
                f"{summary_data['net_profit']} Kenyan Shillings. The business performance indicates "
                f"{summary_data['net_profit_margin_percent']} %. The business performance indicates "
                f"{'strong profitability due to minimal expenses' if float(summary_data['total_expenses']) == 0 else 'operational efficiency and profitability'}. "
                f"Key focus going forward could be maintaining this margin and optimizing future expenditure."
            )

            summarizer = pipeline("summarization", model=settings.HUGGINGFACE_SUMMARY_MODEL)
            summary_list = summarizer(
                text_to_summarize,
                max_length=120,  # You can tweak this to allow more detail
                min_length=30,
                do_sample=False
            )
            return summary_list[0]['summary_text']
        except Exception as e:
            return f"AI summary unavailable: {str(e)}"

class FinancialGraphAPIView(View):
    def get(self, request):
        today = now().date()
        start_date = today - timedelta(days=6)  # Last 7 days
        labels = []
        revenues = []
        expenses = []
        profits = []

        for i in range(7):
            day = start_date + timedelta(days=i)
            labels.append(day.strftime('%Y-%m-%d'))

            daily_revenue = Invoice.objects.filter(
                status='paid',
                date_issued=day
            ).aggregate(total=Sum('total_due'))['total'] or 0

            daily_expense = (
                Expense.objects.filter(date=day).aggregate(total=Sum('amount'))['total'] or 0
            ) + (
                GeneralExpense.objects.filter(date=day).aggregate(total=Sum('amount'))['total'] or 0
            )

            revenues.append(daily_revenue)
            expenses.append(daily_expense)
            profits.append(daily_revenue - daily_expense)

        graph_base64 = generate_financial_line_chart(labels, revenues, expenses, profits)

        return JsonResponse({
            "start_date": str(start_date),
            "end_date": str(today),
            "labels": labels,
            "revenue_data": revenues,
            "expense_data": expenses,
            "profit_data": profits,
            "graph_image_base64": graph_base64
        })