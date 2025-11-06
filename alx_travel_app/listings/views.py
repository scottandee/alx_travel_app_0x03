from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .serializers import UserSerializer, BookingSerializer, ListingSerializer, PaymentSerializer
from .models import User, Booking, Listing, Review, Payment
from .permissions import IsGuestForBooking, IsHostForListing
import requests
import json
import uuid
import alx_travel_app.settings as settings


CHAPA_SECRET_KEY = settings.env('CHAPA_SECRET_KEY')


class ListingViewSets(viewsets.ModelViewSet):
    serializer_class = ListingSerializer
    queryset = Listing.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsHostForListing]

    def perform_create(self, serializer):
        """
        Assign the logged-in user as the listing owner.
        """
        serializer.save(host=self.request.user)


class BookingViewSets(viewsets.ModelViewSet):
    """
    Viewsets for the Bookings model
    """

    serializer_class = BookingSerializer
    queryset = Booking.objects.all()
    permission_classes = [IsAuthenticated, IsGuestForBooking]

    def perform_create(self, serializer):
        """
        Assign booking to logged-in user
        """
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """
        Ensure a user only sees their own bookings.
        """
        user = self.request.user
        if user.role == 'guest':
            return Booking.objects.filter(user=user)
        elif user.role == 'host':
            return Booking.objects.filter(listing_id__host_id=user)
        return Booking.objects.none()


class ReviewViewSets(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = Review.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsGuestForBooking])
def initiate_payment(request, format=None):
    """Initiate Chapa checkout"""
    # Ensure booking_id is part of body
    booking_id = request.data.get("booking")
    if not booking_id:
        return Response({"error": "booking id required"},
                        status=status.HTTP_400_BAD_REQUEST)

    # Retrieve booking with provided id
    try:
        booking = Booking.objects.only(
            "total_price").get(booking_id=booking_id)
    except Booking.DoesNotExist as e:
        return Response({"error": "booking not found"},
                        status=status.HTTP_400_BAD_REQUEST)

    # Define parameters for API call
    url = "https://api.chapa.co/v1/transaction/initialize"

    tx_ref = uuid.uuid4()
    amount = booking.total_price

    payload = {
        "amount": str(amount),
        "currency": "USD",
        "tx_ref": str(tx_ref),
    }
    headers = {
        "Authorization": f"Bearer {CHAPA_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    # API call
    try:
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        print(response_data)
    except requests.RequestException as exc:
        return Response({"error": "payment provider unreachable"},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except ValueError:
        return Response({"error": "invalid response from payment provider"},
                        status=status.HTTP_502_BAD_GATEWAY)

    # Catch request failure
    if response_data.get("status") == "failed":
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    # Save payment to database
    serializer = PaymentSerializer(data={
        **request.data,
        "tx_ref": tx_ref,
        "amount": amount,
    })
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsGuestForBooking])
def verify_payment(request, tx_ref, format=None):
    """Verify Chapa payment"""
    # Ensure tx_ref is valid
    try:
        payment = Payment.objects.get(tx_ref=tx_ref)
    except Payment.DoesNotExist as e:
        return Response(e.errors, status=status.HTTP_404_NOT_FOUND)

    # Declare parameters for API call
    url = f"https://api.chapa.co/v1/transaction/verify/{tx_ref}"
    headers = {
        'Authorization': f'Bearer {CHAPA_SECRET_KEY}'
    }

    # Chapa API call
    try:
        response = requests.get(url, headers=headers)
        response_data = response.json()
    except requests.RequestException as e:
        return Response({"error": "payment provider unreachable"},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except ValueError:
        return Response({"error": "invalid response from payment provider"},
                        status=status.HTTP_502_BAD_GATEWAY)

    if response_data.get("status") == "failed":
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    # Update payment status
    if response_data['data']["status"] == 'success':
        payment.status = Payment.PaymentStatus.SUCCESS
        payment.save()
    elif response_data['data']["status"] == 'failed/cancelled':
        payment.status = Payment.PaymentStatus.FAILED
        payment.save()
    serializer = PaymentSerializer(payment)
    return Response(serializer.data, status=status.HTTP_200_OK)
