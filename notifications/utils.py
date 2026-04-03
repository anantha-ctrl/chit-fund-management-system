import logging
from django.conf import settings

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

def send_payment_reminder(payment):
    """Sends a standardized due date reminder."""
    message = f"Hello {payment.member.name}, reminder for your Chit Group {payment.chit_group.name}. " \
              f"Installment #{payment.installment_number} of ₹{payment.amount} is due on {payment.due_date}. " \
              f"Please pay on time to avoid penalties. - SmartChit"
    return send_sms(payment.member.phone, message)

def send_auction_alert(chit_group, auction_date):
    """Sends auction notification to all group members."""
    message = f"SmartChit Alert: Auction for group {chit_group.name} is scheduled for {auction_date.strftime('%d %b %Y')}. " \
              f"Be ready to bid! - SmartChit"
    
    results = []
    for member in chit_group.members.all():
        results.append(send_sms(member.phone, message))
    return all(results)
