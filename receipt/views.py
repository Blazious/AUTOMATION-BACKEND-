from rest_framework import viewsets, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Receipt
from .serializers import ReceiptSerializer
from .utils import generate_receipt_pdf
from django.http import FileResponse
from django.shortcuts import get_object_or_404




#DEFINED VIEWS 
class ReceiptViewSet(viewsets.ModelViewSet):
    queryset = Receipt.objects.all().select_related('invoice', 'client', 'created_by')
    serializer_class = ReceiptSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
  

    
def receipt_pdf_view(request, receipt_id):
    receipt = get_object_or_404(Receipt, id=receipt_id)
    pdf_buffer = generate_receipt_pdf(receipt)
    return FileResponse(pdf_buffer, as_attachment=True, filename=f"{receipt.receipt_number}.pdf")