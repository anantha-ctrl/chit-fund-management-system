from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

# Configure logging
logger = logging.getLogger(__name__)

def send_sms(phone_number, message):
    """
    Utility function to send SMS. 
    Plug in your preferred API (Twilio, MSG91, Textlocal, etc.) here.
    """
    # Standardizing phone number (Indian context example)
    if not phone_number.startswith('+'):
        if len(phone_number) == 10:
            phone_number = f"+91{phone_number}"

    # --- PLUG IN YOUR API LOGIC HERE ---
    # Example for logging/audit purposes instead of actual costing API calls during development
    logger.info(f"SMS SENT TO {phone_number}: {message}")
    
    # Mock return
    return True

def send_whatsapp_message(phone_number, message):
    """
    Utility function to send WhatsApp.
    Placeholder for WhatsApp API (Meta Business, Twilio, or WAMAPI).
    Currently generates click-to-chat links for user interactions.
    """
    # Standardizing phone number
    clean_phone = ''.join(filter(str.isdigit, str(phone_number)))
    if len(clean_phone) == 10:
        clean_phone = f"91{clean_phone}"
    
    # URL encoded message for the link
    import urllib.parse
    encoded_message = urllib.parse.quote(message)
    whatsapp_url = f"https://wa.me/{clean_phone}?text={encoded_message}"
    
    # For actual API integration, you would use requests to post to an endpoint here.
    logger.info(f"WHATSAPP READY TO SEND TO {clean_phone}: {message}")
    
    return whatsapp_url, True

def send_payment_reminder(payment):
    """Sends a standardized due date reminder via SMS & log WhatsApp."""
    message = f"Hello {payment.member.name}, reminder for your Chit Group {payment.chit_group.name}. " \
              f"Installment #{payment.installment_number} of ₹{payment.amount} is due on {payment.due_date}. " \
              f"Please pay on time to avoid penalties. - SmartChit"
    
    send_sms(payment.member.phone, message)
    send_whatsapp_message(payment.member.phone, message)
    return True

def send_auction_alert(chit_group, auction_date):
    """Sends auction notification to all group members."""
    message = f"SmartChit Alert: Auction for group {chit_group.name} is scheduled for {auction_date.strftime('%d %b %Y')}. " \
              f"Be ready to bid! - SmartChit"
    
    results = []
    for member in chit_group.members.all():
        results.append(send_sms(member.phone, message))
    return all(results)

def send_payment_receipt_email(payment):
    """
    Sends a professional HTML receipt to the member after successful payment.
    Requires member.user.email to be set.
    """
    if not payment.member.user or not payment.member.user.email:
        return False
        
    subject = f"Payment Receipt - {payment.chit_group.name} (Inst #{payment.installment_number})"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = payment.member.user.email
    
    context = {
        'payment': payment,
        'member': payment.member,
        'group': payment.chit_group,
        'date': payment.payment_date or payment.created_at,
    }
    
    html_content = render_to_string('notifications/emails/payment_receipt.html', context)
    text_content = strip_tags(html_content)
    
    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
