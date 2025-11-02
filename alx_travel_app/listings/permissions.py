from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Listing, Booking


class IsGuestForBooking(BasePermission):
    """
    This class defines permissions for the bookings view

    has_permission: Allow only users with role='guest' to
    create a booking.

    has_object_permission: Allow only owners of a booking to
    retrieve/update/delete.
    """

    def has_permission(self, request, view):
        # Allow only guests to create
        if request.method == 'POST':
            return request.user.is_authenticated and request.user.role == 'guest'
        return True

    def has_object_permission(self, request, view, obj):
        # Allow only owners to retrieve/delete booking
        return obj.user_id == request.user


class IsHostForListing(BasePermission):
    """
    This class defines permissions for the bookings view

    has_permission: Allow only users with role='host' to
    create a listing.

    has_object_permission: Allow only owners of a listing to
    retrieve/update/delete.
    """

    def has_permission(self, request, view):
        # Allow only hosts to create listing
        if request.method == 'POST':
            return request.user.role == 'host'
        return True

    def has_object_permission(self, request, view, obj):
        # Allow only owners to retrieve/delete booking
        return obj.host == request.user
