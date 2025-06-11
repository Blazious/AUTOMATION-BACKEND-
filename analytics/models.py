from invoice.models import Invoice
from expenses.models import Expense, GeneralExpense
from django.db.models import Sum
from django.utils.timezone import now
from datetime import timedelta
from collections import defaultdict

def get_financial_summary(start_date=None, end_date=None):
    if not start_date or not end_date:
        today = now().date()
        start_date = today.replace(day=1)
        end_date = today

    # Revenue from paid invoices
    invoices = Invoice.objects.filter(
        status='paid',
        date_issued__range=(start_date, end_date)
    )
    total_revenue = invoices.aggregate(total=Sum('total_due'))['total'] or 0

    # Total expenses from two sources
    expenses = Expense.objects.filter(date__range=(start_date, end_date))
    general_expenses = GeneralExpense.objects.filter(date__range=(start_date, end_date))
    
    total_expense = (
        expenses.aggregate(total=Sum('amount'))['total'] or 0
    ) + (
        general_expenses.aggregate(total=Sum('amount'))['total'] or 0
    )

    # Net profit
    net_profit = total_revenue - total_expense


    if total_revenue > 0:
        profit_margin = (net_profit / total_revenue) * 100
    else:
        profit_margin = 0



    return {
        'start_date': start_date,
        'end_date': end_date,
        'total_revenue': total_revenue,
        'total_expense': total_expense,
        'net_profit': net_profit,
        'net_profit_margin_percent': round(profit_margin, 2), 

    }
