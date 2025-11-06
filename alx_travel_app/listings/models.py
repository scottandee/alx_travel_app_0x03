import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator


class UserRole(models.TextChoices):
    GUEST = 'guest'
    HOST = 'host'
    ADMIN = 'admin'


class User(AbstractUser):
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    role = models.CharField(max_length=20, choices=UserRole.choices)
    created_at = models.DateTimeField(auto_now_add=True)


class Listing(models.Model):
    listing_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    host = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="listings")
    name = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - ${self.price} ({self.location})"


class BookingStatus(models.TextChoices):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'


class Booking(models.Model):
    booking_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="bookings")
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bookings")
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.start_date and self.end_date and self.listing:
            days = (self.end_date - self.start_date).days
            self.total_price = self.listing.price_per_night * days
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking_id} - ${self.total_price} ({self.status})"


class Review(models.Model):
    review_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="listings")
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews")
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)])
    comment = models.TextField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)


class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending'
        SUCCESS = 'success'
        FAILED = 'failed'
    payment_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    tx_ref = models.UUIDField(unique=True)
    booking = models.ForeignKey(
        Booking,
        related_name='payments',
        on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    status = models.CharField(
        max_length=10,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
