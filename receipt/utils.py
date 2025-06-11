import os
from io import BytesIO
from decimal import Decimal
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Flowable,HRFlowable
)
from reportlab.lib.units import inch
from num2words import num2words






def amount_to_kes_words(amount):
    """
    Convert amount to words in Kenyan Shillings format
    Example: 1234.56 -> "One Thousand Two Hundred Thirty-Four Kenyan Shillings and Fifty-Six Cents Only"
    """
    def convert_less_than_one_thousand(n):
        ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
                "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
                "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", 
                "Eighty", "Ninety"]

        if n == 0:
            return ""
        if n < 20:
            return ones[n]
        if n < 100:
            return tens[n // 10] + (" " + ones[n % 10] if n % 10 != 0 else "")
        if n < 1000:
            return ones[n // 100] + " Hundred" + (" " + convert_less_than_one_thousand(n % 100) if n % 100 != 0 else "")
        return ""

    try:
        # Split into whole and decimal parts
        whole = int(amount)
        cents = int(round((amount - whole) * 100))
        
        if whole == 0 and cents == 0:
            return "Zero Kenyan Shillings Only"
        
        # Convert whole part to words
        if whole == 0:
            whole_words = ""
        else:
            units = ["", "Thousand", "Million", "Billion", "Trillion"]
            whole_words = ""
            unit_index = 0
            
            while whole > 0:
                chunk = whole % 1000
                if chunk != 0:
                    chunk_words = convert_less_than_one_thousand(chunk)
                    if unit_index > 0:
                        chunk_words += " " + units[unit_index]
                    whole_words = chunk_words + " " + whole_words
                whole = whole // 1000
                unit_index += 1
            
            whole_words = whole_words.strip() + " Kenyan Shillings"
        
        # Convert cents part to words
        if cents > 0:
            cents_words = convert_less_than_one_thousand(cents) + " Cents"
            if whole_words:
                result = f"{whole_words} and {cents_words}"
            else:
                result = cents_words
        else:
            result = whole_words
        
        return f"{result} Only".strip()
    
    except Exception as e:
        print(f"Error converting amount to words: {e}")
        return f"{amount:.2f} Kenyan Shillings Only"


















class DottedBox(Flowable):
    def __init__(self, width, height):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def draw(self):
        self.canv.setDash(3, 2)
        self.canv.rect(0, 0, self.width, self.height)

class SignatureLine(Flowable):
    def __init__(self, width, label):
        Flowable.__init__(self)
        self.width = width
        self.label = label

    def draw(self):
        self.canv.line(0, 0, self.width, 0)
        self.canv.drawString(0, -12, self.label)

def generate_receipt_pdf(receipt):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=30, leftMargin=30,
                            topMargin=30, bottomMargin=18)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CenterBoldGreen', alignment=TA_CENTER, fontSize=14, leading=16, textColor=colors.green, spaceAfter=10, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='RightNormal', alignment=TA_RIGHT, fontSize=10, leading=12))

    elements = []

    # Path to the logo
    logo_path = os.path.join(settings.BASE_DIR, 'invoice', 'static', 'images', 'logo.png')
    if os.path.exists(logo_path):
        img = Image(logo_path, width=1.5 * inch, height=1.5 * inch)
        img.hAlign = 'RIGHT'
        elements.append(img)
    else:
        elements.append(Paragraph("<b>LOGO MISSING</b>", styles['RightNormal']))

    # Company Header
    elements.append(Paragraph("EcoWaste Solutions Ltd", styles['CenterBoldGreen']))
    elements.append(Paragraph("P.O BOX 12345, Nairobi", styles['Normal']))
    elements.append(Paragraph("Phone: (+254) 700 123 456 | Email: info@ecowaste.co.ke", styles['Normal']))
    elements.append(Paragraph("KRA PIN : P051234567X", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Receipt Title
    elements.append(Paragraph("<b>PAYMENT RECEIPT</b>", styles['CenterBoldGreen']))
    elements.append(Paragraph(f"Receipt No: {receipt.receipt_number}", styles['Normal']))
    elements.append(Paragraph(f"Date Paid: {receipt.date_paid.strftime('%B %d, %Y')}", styles['Normal']))
    elements.append(Paragraph(f"Payment Method: {receipt.get_payment_method_display()}", styles['Normal']))
    elements.append(Paragraph(f"Issued At: {receipt.created_at.strftime('%B %d, %Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Client Information
    client = receipt.client
    client_data = [
        ['Client Information', ''],
        ['Name:', client.name],
        ['Address:', client.address],
        ['Contact:', f"{client.name} ({client.phone})"],
        ['Client ID:', str(client.id)],
        ['KRA PIN:', client.kra_pin if client.kra_pin else 'N/A'],
    ]
    client_table = Table(client_data, colWidths=[100, 350])
    client_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.green),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(client_table)
    elements.append(Spacer(1, 12))

    # Invoice Info
    invoice = receipt.invoice
    invoice_data = [
        ['Invoice Details', ''],
        ['Invoice No:', invoice.invoice_number],
        ['Invoice Date:', invoice.date_issued.strftime('%B %d, %Y')],
        ['Invoice Amount:', f"KES {invoice.total_due:.2f}"],
    ]
    invoice_table = Table(invoice_data, colWidths=[100, 350])
    invoice_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.green),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(invoice_table)
    elements.append(Spacer(1, 12))

    # Payment Details
    payment_status = "FULLY PAID" if receipt.amount >= invoice.total_due else f"Balance Due: KES {invoice.balance_due:.2f}"
    payment_data = [
        ['Payment Details', ''],
        ['Received By:', receipt.created_by.get_full_name() if receipt.created_by else "N/A"],
        ['Payment Date:', receipt.date_paid.strftime('%B %d, %Y')],
        [f"Invoice {invoice.invoice_number}", f"KES {receipt.amount:.2f}"],
        ['Amount Paid:', f"KES {receipt.amount:.2f}"],
        ['Status:', payment_status],
    ]
    payment_table = Table(payment_data, colWidths=[150, 300])
    payment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.green),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(payment_table)
    elements.append(Spacer(1, 24))

    # Amount in Words
    amount_words = amount_to_kes_words(float(receipt.amount))
    elements.append(Paragraph(f"Amount in Words: <b>{amount_words}</b>", styles['Normal']))
    elements.append(Spacer(1, 24))

    # Signatures and Stamp
    elements.append(Spacer(1, 24))  # More space before the stamp box

    # Dotted box for stamp
    elements.append(DottedBox(2.5 * inch, 1 * inch))
    elements.append(Spacer(1, 12))

    # Official Stamp Label
    elements.append(SignatureLine(2.5 * inch, "Official Stamp"))
    elements.append(Spacer(1, 36))  # More spacing before next line

    # Client Signature Line

    signature_path = os.path.join(
        settings.BASE_DIR,      # same BASE_DIR you used for the logo
        'receipt',              # <-- keep if your signature lives in invoice/static/images/
        'static',
        'imagez',               # NOTE the *plural* 'images'
        'signature.png'
    )

    if os.path.exists(signature_path):
        sig_img = Image(signature_path, width=2 * inch, height=1 * inch)
        sig_img.hAlign = 'LEFT'        # or 'RIGHT' / 'CENTER' as you prefer
        elements.append(sig_img)
    else:
        elements.append(
            )
        
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("_________________________", styles['Normal']))
    elements.append(Paragraph("Authorised Signature", styles['Normal']))
    elements.append(Spacer(1, 36))

    # Authorized Signature Line
    # Add signature line
    elements.append(HRFlowable(thickness=1, color=colors.black))
    elements.append(Spacer(1, 4))



    # Add the actual name below the label
    elements.append(Paragraph(receipt.created_by.get_full_name() if receipt.created_by else "N/A", styles['Normal']))
    elements.append(Spacer(1, 24))


    # Footer Notes
    elements.append(Paragraph("This receipt serves as confirmation of payment received.", styles['Normal']))
    elements.append(Paragraph("For any inquiries, contact accounts@ecowaste.com", styles['Normal']))
    elements.append(Paragraph("This is an automatically generated document. No signature is required for electronic versions.", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer
