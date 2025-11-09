from celery import shared_task
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils import timezone
from listings.models import Payment


@shared_task
def send_booking_confirmation(email: str, payment_id: str):
    """
    Send booking confirmation email in HTML format only.
    payment_id = UUID of the Payment instance.
    """

    try:
        payment = Payment.objects.select_related(
            "booking",
            "booking__listing",
            "booking__user"
        ).get(payment_id=payment_id)
    except Payment.DoesNotExist:
        return "payment_not_found"

    booking = payment.booking
    listing = booking.listing
    user = booking.user

    context = {
        "user": user,
        "booking": booking,
        "listing": listing,
        "payment": payment,
        "now": timezone.now(),
    }

    subject = f"Booking Confirmed — Receipt for {booking.booking_id}"
    html_body = render_to_string("emails/booking_confirmation.html", context)

    msg = EmailMessage(
        subject=subject,
        body=html_body,
        to=[email],
    )
    msg.content_subtype = "html"
    msg.send()

    return f"Email sent to {email}"
