from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListingViewSets, BookingViewSets, ReviewViewSets, initiate_payment, verify_payment

router = DefaultRouter(trailing_slash=False)
router.register(r'listings', ListingViewSets, basename='listings')
router.register(r'bookings', BookingViewSets, basename='bookings')
router.register(r'reviews', ReviewViewSets, basename='reviews')

urlpatterns = [
    path('', include(router.urls)),
    path('payments/initiate/', view=initiate_payment),
    path('payments/verify/<uuid:tx_ref>/', view=verify_payment)
]
