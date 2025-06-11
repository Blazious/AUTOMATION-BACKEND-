import io
from datetime import datetime
from decimal import Decimal
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from django.conf import settings
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER 
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Flowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.contrib.staticfiles import finders

from reportlab.rl_config import defaultPageSize

# Optional: Register a TTF font for nicer fonts (if you want)
# pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))

PAGE_WIDTH, PAGE_HEIGHT = A4


class HorizontalLine(Flowable):
    """Draw a horizontal line"""
    def __init__(self, width=450):
        Flowable.__init__(self)
        self.width = width
        self.height = 1

    def draw(self):
        self.canv.line(0, 0, self.width, 0)


def generate_invoice_pdf(invoice):
    """
    Generates a PDF invoice for the given Invoice object using ReportLab.
    Returns HttpResponse with PDF for downloading.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=20*mm, leftMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)

    styles = getSampleStyleSheet()
    normal = styles['Normal']
    heading = styles['Heading1']
    heading.alignment = 1  # center
  



    logo_path = finders.find("images/logo.png")
    
    if logo_path:
       try:
           logo = Image(logo_path, width=2 * inch, height=1 * inch)
           elements.append(logo)
           elements.append(Spacer(1, 0.25 * inch))  # Add some space after logo
       except Exception as e:
           print(f"Could not load logo image: {e}")
       else:
           print("Logo path could not be found.")
   
    # Custom styles
    bold = ParagraphStyle('Bold', parent=normal, fontName='Helvetica-Bold')
    small = ParagraphStyle('small', parent=normal, fontSize=8)
    small_bold = ParagraphStyle('small_bold', parent=bold, fontSize=8)
    right_align = ParagraphStyle('right', parent=normal, alignment=2)
    right_bold = ParagraphStyle('right_bold', parent=bold, alignment=2)
    red_text = ParagraphStyle('red', parent=normal, textColor=colors.red)
    italic = ParagraphStyle(
    'Tagline',
    parent=normal,
    fontSize=8,
    fontName='Helvetica-Oblique',
    leading=10,
    alignment=0  # Left-align inside nested table
    )
   

    # Company Info & Logo Placeholder (You can replace with Image(path))

    elements = []

                # --- Load logo ---
    logo_path = finders.find("images/logo.png")
    logo_content = []

    if logo_path:
        try:
            # Logo image
            logo_img = Image(logo_path, width=1.5 * inch, height=0.75 * inch)
            # Tagline paragraph
            tagline = Paragraph("your one stop shop for waste solutions!", italic)

            # Combine logo and tagline in one row using nested table
            logo_and_tagline = Table([[logo_img, tagline]], colWidths=[1.5 * inch, 2.5 * inch])
            logo_and_tagline.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))

            right_column = logo_and_tagline

        except Exception as e:
            print(f"Could not load logo image: {e}")
            right_column = ""
    else:
        right_column = ""

    # --- Company Info Table ---
    company_info = Table([
        [Paragraph("<b>EcoWaste Solutions Ltd</b>", bold)],
        [Paragraph("P.O. Box 12345, Nairobi", normal)],
        [Paragraph("Tel: +254 700 123 456", normal)],
        [Paragraph("Email: info@ecowaste.co.ke", normal)],
        [Paragraph("KRA PIN: P051234567X", normal)],
    ], colWidths=[4 * inch])

    # --- Header Table ---
    header_table = Table([
        [company_info, right_column]
    ],
    colWidths=[4 * inch, 3.5 * inch],  # Adjusted right column width
    rowHeights=[1.4 * inch]
    )

    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (0, 0), 0),
        ('RIGHTPADDING', (1, 0), (1, 0), 0),
    ]))

    # --- Assemble PDF content ---
    elements.append(header_table)
    elements.append(Spacer(1, 0.2 * inch))

    # Horizontal line (you should define this function/class)
    elements.append(HorizontalLine(width=7 * inch))  # Assuming HorizontalLine is defined elsewhere
    elements.append(Spacer(1, 0.3 * inch)) 

    
    # Invoice title and meta data
    elements.append(Paragraph("<b>INVOICE</b>", heading))
    elements.append(Spacer(1, 10))



    # Add disclaimer about eTIMS
    etims_notice = Paragraph(
        "This invoice will be submitted to eTIMS for tax compliance purposes.<br/>"
        "<i>This is an internal invoice. An official eTIMS Tax Invoice will follow for compliance and input claim purposes.</i>",
        ParagraphStyle(
            'etimsNote',
            parent=normal,
            fontSize=9,
            leading=11,
            textColor=colors.grey,
            alignment=TA_CENTER 
        )
    )
    elements.append(etims_notice)
    elements.append(Spacer(1, 10))



    # Invoice #, Date, Due Date
    inv_num = invoice.invoice_number or "N/A"
    date_issued = invoice.date_issued.strftime("%B %d, %Y")
    due_date = invoice.due_date.strftime("%B %d, %Y")

    meta_data_table = Table([
        ["Invoice #:", inv_num],
        ["Date:", date_issued],
        ["Due Date:", due_date],
    ], colWidths=[80*mm, 80*mm])
    meta_data_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(meta_data_table)
    elements.append(Spacer(1, 15))

    # BILL TO:
    client = invoice.client
    client_wht_agent = " * Withholding VAT Agent" if client.wht_agent else ""
    client_kra_pin = client.kra_pin or "N/A"

    billing_info = [
        [Paragraph("<b>BILL TO:</b>", bold)],
        [client.name + client_wht_agent],
        [client.address],
        [f"Tel: {client.phone}"],
        [f"Email: {client.email}"],
        [f"KRA PIN: {client_kra_pin}"]
    ]

    billing_table = Table(billing_info, colWidths=[160*mm])
    billing_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(billing_table)
    elements.append(Spacer(1, 20))

    # SERVICE DETAILS heading
    elements.append(Paragraph("<b>SERVICE DETAILS:</b>", bold))
    elements.append(Spacer(1, 6))

    # Collection info from linked collection
    collection = invoice.collection
    if collection:
        # Use collection date, due date, location (from collection.client.address maybe),
        # service type (hardcoded "Waste Collection" for now), waste category from items

        collection_date = collection.date_collected.strftime("%B %d, %Y")
        service_type = "Waste Collection"
        location = client.city + " Office" if client.city else "N/A"

        # Waste category - if multiple items with different categories, join with commas
        waste_categories = set(item.get_waste_category_display() for item in collection.items.all())
        waste_category_str = ", ".join(waste_categories) if waste_categories else "N/A"

        service_details = [
            ["Collection Date:", collection_date],
            ["Service Type:", service_type],
            ["Location:", location],
            ["Waste Category:", waste_category_str]
        ]

        service_table = Table(service_details, colWidths=[80*mm, 80*mm])
        service_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(service_table)
    else:
        elements.append(Paragraph("No linked collection for this invoice.", normal))

    elements.append(Spacer(1, 15))

    # Line items table header
    line_items_header = [
        'Description', 'Quantity', 'Unit', 'Rate per Unit (KES)', 'Amount (KES)'
    ]
    line_items_data = [line_items_header]

    # Fill line items from InvoiceItems
    for item in invoice.items.all():
        line_items_data.append([
            item.description,
            f"{item.quantity:.3f}",
            item.unit,
            f"{item.unit_price:,.2f}",
            f"{item.amount:,.2f}",
        ])

    # Table styles
    tbl_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ])

    items_table = Table(line_items_data, colWidths=[70*mm, 25*mm, 30*mm, 40*mm, 40*mm])
    items_table.setStyle(tbl_style)
    elements.append(items_table)
    elements.append(Spacer(1, 12))

    # Subtotal, VAT, Gross Total, Less WHT, Net Due
    subtotal = invoice.subtotal
    vat = invoice.vat
    wht = invoice.wht
    gross_total = subtotal + vat
    net_due = invoice.total_due

    summary_data = [
        ["Subtotal:", f"KES {subtotal:,.2f}"],
        ["VAT (16%):", f"KES {vat:,.2f}"],
        ["Gross Total:", f"KES {gross_total:,.2f}"],
        ["Less: Withholding VAT (2%):", f"KES ({wht:,.2f})"],
        [Paragraph("<b>NET AMOUNT DUE:</b>", bold), Paragraph(f"KES {net_due:,.2f}", bold)]
    ]

    summary_table = Table(summary_data, colWidths=[150*mm, 65*mm])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 15))

    # WITHHOLDING VAT NOTICE block
    wht_notice = """
    <b>⚠️ WITHHOLDING VAT NOTICE:</b><br/>
    As a registered Withholding VAT Agent, you are required to:<br/>
    &bull; Pay us: KES {net_due:,.2f}<br/>
    &bull; Remit to KRA: KES {wht:,.2f} (Withholding VAT on our behalf)<br/>
    &bull; Provide us with a Withholding VAT Certificate for our records
    """.format(net_due=net_due, wht=wht)

    elements.append(Paragraph(wht_notice, normal))
    elements.append(Spacer(1, 15))

    # PAYMENT TERMS & BANKING DETAILS block
    payment_terms = """
    <b>PAYMENT TERMS & BANKING DETAILS:</b><br/>
    Payment Due: 14 days from invoice date<br/>
    Bank: KCB Bank Kenya Ltd<br/>
    Account Name: EcoWaste Solutions Ltd<br/>
    Account Number: 1234567890<br/>
    Branch: Westlands Branch<br/>
    <br/>
    Late Payment: 2% monthly interest on overdue amounts<br/>
    Currency: All amounts in Kenya Shillings (KES)<br/>
    This invoice will be submitted to eTIMS for tax compliance purposes.<br/>
    Official eTIMS tax invoice will be provided separately for your records.
    """

    elements.append(Paragraph(payment_terms, normal))
    elements.append(Spacer(1, 15))

    # Footer thank you note
    thank_you = "Thank you for choosing EcoWaste Solutions Ltd"
    elements.append(Paragraph(thank_you, bold))

    # Build PDF
    doc.build(elements)

    buffer.seek(0)
    return buffer


def invoice_pdf_response(invoice):
    """Return HttpResponse with PDF file to download for given Invoice instance"""
    pdf_buffer = generate_invoice_pdf(invoice)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    filename = f"Invoice_{invoice.invoice_number}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

