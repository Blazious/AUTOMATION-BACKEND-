from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Invoice
from .serializers import InvoiceSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .utils import generate_invoice_pdf
from django.shortcuts import get_object_or_404
from django.http import FileResponse




class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all().order_by('-date_issued')
    serializer_class = InvoiceSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'client']
    search_fields = ['invoice_number', 'client__name']
    ordering_fields = ['date_issued', 'due_date', 'total_due']

    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, pk=None):
        invoice = self.get_object()
        invoice.status = 'paid'
        invoice.save()
        serializer = self.get_serializer(invoice)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


def invoice_pdf_view(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    pdf_buffer = generate_invoice_pdf(invoice)
    response = FileResponse(pdf_buffer, as_attachment=True, filename=f"Invoice_{invoice.invoice_number}.pdf")
    return response