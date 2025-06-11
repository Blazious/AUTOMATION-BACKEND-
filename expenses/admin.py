from django.contrib import admin
from .models import Expense, GeneralExpense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'collection_display',
        'category',
        'description',
        'amount',
        'reference',
    )
    list_filter = ('category', 'date', 'collection',)
    search_fields = ('description', 'reference', 'collection__id',)
    readonly_fields = ('created_at',)
    list_per_page = 25

    def collection_display(self, obj):
        return f"#COL-{obj.collection.id:04d}" if obj.collection else "- General -"
    collection_display.short_description = 'Collection ID'


# ✅ New Admin for GeneralExpense
@admin.register(GeneralExpense)
class GeneralExpenseAdmin(admin.ModelAdmin):
    list_display = ('date', 'description', 'amount', 'receipt')
    search_fields = ('description',)
    list_filter = ('date',)
    list_per_page = 25