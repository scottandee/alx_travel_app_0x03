from django.core.management.base import BaseCommand
from django_seed import Seed
from listings.models import User, Listing, Booking, Review
import random
from datetime import timedelta, date
import uuid


class Command(BaseCommand):
    help = "Seed database with sample data"

    def handle(self, *args, **kwargs):
        seeder = Seed.seeder()

        # Create Users
        seeder.add_entity(User, 2, {
            "user_id": lambda x: uuid.uuid4(),
            "username": lambda x: seeder.faker.user_name(),
            "first_name": lambda x: seeder.faker.first_name(),
            "last_name": lambda x: seeder.faker.last_name(),
            "email": lambda x: seeder.faker.unique.email(),
            "password": lambda x: "pass123",
            "phone_number": lambda x: seeder.faker.phone_number(),
            "role": lambda x: "host",
            "created_at": lambda x: seeder.faker.date_time_this_year(),
        })

        seeder.add_entity(User, 2, {
            "user_id": lambda x: uuid.uuid4(),
            "username": lambda x: seeder.faker.user_name(),
            "first_name": lambda x: seeder.faker.first_name(),
            "last_name": lambda x: seeder.faker.last_name(),
            "email": lambda x: seeder.faker.unique.email(),
            "password": lambda x: "pass123",
            "phone_number": lambda x: seeder.faker.phone_number(),
            "role": lambda x: "guest",
            "created_at": lambda x: seeder.faker.date_time_this_year(),
        })

        seeder.add_entity(User, 1, {
            "user_id": lambda x: uuid.uuid4(),
            "username": lambda x: seeder.faker.user_name(),
            "first_name": lambda x: seeder.faker.first_name(),
            "last_name": lambda x: seeder.faker.last_name(),
            "email": lambda x: seeder.faker.unique.email(),
            "password": lambda x: "pass123",
            "phone_number": lambda x: seeder.faker.phone_number(),
            "role": lambda x: "admin",
            "created_at": lambda x: seeder.faker.date_time_this_year(),
        })

        inserted = seeder.execute()

        # Hash passwords for all created users
        for user_id in inserted[User]:
            user = User.objects.get(pk=user_id)
            user.set_password("pass123")
            user.save()

        # Fetch created users
        users = list(User.objects.all())
        hosts = [u for u in users if u.role == "host"]
        guests = [u for u in users if u.role == "guest"]

        # Create Listings for hosts
        for i in range(10):
            listing = Listing.objects.create(
                listing_id=uuid.uuid4(),
                host=random.choice(hosts),
                name=f"Property {i+1}",
                description=seeder.faker.text(max_nb_chars=200),
                location=seeder.faker.city(),
                price_per_night=random.randint(50, 500),
                created_at=seeder.faker.date_time_this_year(),
                updated_at=seeder.faker.date_time_this_year(),
            )

            # Create Booking for each listing
            guest = random.choice(guests)
            start = date.today() + timedelta(days=random.randint(1, 30))
            end = start + timedelta(days=random.randint(2, 7))
            Booking.objects.create(
                booking_id=uuid.uuid4(),
                listing=listing,
                user=guest,
                start_date=start,
                end_date=end,
                total_price=(listing.price_per_night * (end - start).days),
                status=random.choice(["pending", "confirmed", "cancelled"]),
                created_at=seeder.faker.date_time_this_year(),
            )

            # Create Review for each listing
            Review.objects.create(
                review_id=uuid.uuid4(),
                listing=listing,
                user=guest,
                rating=random.randint(1, 5),
                comment=seeder.faker.sentence(nb_words=12),
                created_at=seeder.faker.date_time_this_year(),
            )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully! Passwords hashed."))
