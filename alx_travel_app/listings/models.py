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
