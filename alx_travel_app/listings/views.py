from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .serializers import UserSerializer, BookingSerializer, ListingSerializer
from .models import User, Booking, Listing, Review
from .permissions import IsGuestForBooking, IsHostForListing


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
