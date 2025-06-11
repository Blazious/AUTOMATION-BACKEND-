
from decimal import Decimal
from invoice.models import Invoice
from expenses.models import Expense
from django.db import models
from django.db.models import Sum


def get_financial_summary(start_date=None, end_date=None):
    invoices = Invoice.objects.all()
    expenses = Expense.objects.all()

    if start_date:
        invoices = invoices.filter(date_issued__gte=start_date)
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        invoices = invoices.filter(date_issued__lte=end_date)
        expenses = expenses.filter(date__lte=end_date)

    total_revenue = invoices.aggregate(total=Sum('total_due'))['total'] or Decimal('0.00')
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    net_profit = total_revenue - total_expenses


    if total_revenue > 0:
        net_profit_margin_percent = (net_profit / total_revenue) * 100
    else:
        net_profit_margin_percent = 0.0

    return {
        "total_revenue": str(total_revenue),
        "total_expenses": str(total_expenses),
        "net_profit": str(net_profit),
        'net_profit_margin_percent': net_profit_margin_percent,
        "start_date": str(start_date) if start_date else None,
        "end_date": str(end_date) if end_date else None,
    }