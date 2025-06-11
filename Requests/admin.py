from django.contrib import admin
from .models import ServiceRequest

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('date_received', 'client_display', 'from_client', 'email', 'subject', 'status', 'is_collection_created')
    list_filter = ('status', 'date_received')
    search_fields = ('from_client_name', 'email', 'subject', 'client__name')
    readonly_fields = ('date_received',)
    actions = ['mark_as_read', 'mark_as_responded']

    def client_display(self, obj):
        return obj.client.name if obj.client else '- Not linked -'
    client_display.short_description = 'Client'

    def mark_as_read(self, request, queryset):
        updated = queryset.update(status='read')
        self.message_user(request, f"{updated} request(s) marked as Read.")
    mark_as_read.short_description = "Mark selected requests as Read"

    def mark_as_responded(self, request, queryset):
        updated = queryset.update(status='responded')
        self.message_user(request, f"{updated} request(s) marked as Responded.")
    mark_as_responded.short_description = "Mark selected requests as Responded"


    # Optional: add custom admin URLs for your action buttons (needs extra url handling)
    # This requires overriding get_urls() and adding views to handle the buttons.
