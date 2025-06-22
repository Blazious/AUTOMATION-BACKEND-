import matplotlib
matplotlib.use('Agg') 



import matplotlib.pyplot as plt
import io
import base64

def generate_financial_line_chart(dates, revenues, expenses, profits):
    plt.figure(figsize=(8, 4))
    plt.plot(dates, revenues, label='Revenue', marker='o')
    plt.plot(dates, expenses, label='Expenses', marker='o')
    plt.plot(dates, profits, label='Net Profit', marker='o')
    plt.xlabel('Date')
    plt.ylabel('Amount (KES)')
    plt.title('Financial Summary')
    plt.legend()
    plt.tight_layout()

    # Save plot to a BytesIO buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Encode image to base64
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    buffer.close()
    plt.close()

    return image_base64
