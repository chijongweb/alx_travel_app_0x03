from rest_framework import viewsets
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Payment
from .tasks import send_booking_confirmation_email
import uuid

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

@api_view(['POST'])
def initiate_payment(request):
    chapa_url = "https://api.chapa.co/v1/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {os.getenv('CHAPA_SECRET_KEY')}"
    }

    booking_ref = str(uuid.uuid4())
    amount = request.data.get("amount")
    email = request.data.get("email")

    payload = {
        "amount": amount,
        "currency": "ETB",
        "email": email,
        "tx_ref": booking_ref,
        "callback_url": "http://localhost:8000/listings/verify-payment/"
    }

    response = requests.post(chapa_url, json=payload, headers=headers)
    data = response.json()

    if response.status_code == 200 and data.get("status") == "success":
        Payment.objects.create(
            booking_reference=booking_ref,
            transaction_id=data['data']['tx_ref'],
            amount=amount,
            status="Pending"
        )
        return Response({"checkout_url": data['data']['checkout_url']})
    return Response(data, status=response.status_code)

@api_view(['GET'])
def verify_payment(request):
    tx_ref = request.GET.get("tx_ref")
    verify_url = f"https://api.chapa.co/v1/transaction/verify/{tx_ref}"
    headers = {
        "Authorization": f"Bearer {os.getenv('CHAPA_SECRET_KEY')}"
    }

    response = requests.get(verify_url, headers=headers)
    data = response.json()

    try:
        payment = Payment.objects.get(transaction_id=tx_ref)
        if data['data']['status'] == 'success':
            payment.status = 'Completed'
        else:
            payment.status = 'Failed'
        payment.save()
    except Payment.DoesNotExist:
        return Response({"error": "Payment not found."}, status=404)

    return Response(data)


def perform_create(self, serializer):
    booking = serializer.save()
    email = booking.user.email
    details = str(booking)
    send_booking_confirmation_email.delay(email, details)