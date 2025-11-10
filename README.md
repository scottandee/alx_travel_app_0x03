# ALX Travel App – ProDev Backend (Milestone 4)
### Project Overview
This repository contains the initial setup for the **ALX Travel App**, a real-world Django application that serves as the foundation for a travel listing platform. Milestone 5 focuses on enhancing the alx_travel_app project by implementing asynchronous background processing using `Celery` with `RabbitMQ` as the message broker. The main feature added is an email notification system that sends booking confirmations after payment verification without blocking the main request-response cycle. This ensures improved performance and a better user experience.

## File Structure
```bash
.
├── README.md                             
└── alx_travel_app
    ├── README.md                         
    ├── alx_travel_app
    │   ├── __init__.py
    │   ├── asgi.py
    │   ├── requirement.txt
    │   ├── settings.py                   # Global Django settings
    │   ├── urls.py                       # Project-level URL dispatcher
    │   └── wsgi.py
    ├── listings
    │   ├── __init__.py
    │   ├── admin.py                      
    │   ├── apps.py
    │   ├── celery.py                     # Celery application initialization
    │   ├── fixtures
    │   │   └── example.json              # Example fixture data
    │   ├── management
    │   │   └── commands
    │   │       └── seed.py               # Seeder for populating sample data
    │   ├── migrations                    # Database migrations
    │   │   ├── 0001_initial.py
    │   │   ├── ...
    │   │   ├── 0009_payment.py           
    │   │   ├── 0010_alter_payment_tx_ref.py
    │   │   ├── 0011_alter_payment_tx_ref.py
    │   │   ├── 0012_alter_payment_status.py
    │   │   └── __init__.py
    │   ├── models.py                     # Listing, Booking, Review, Payment, User models
    │   ├── permissions.py                # Custom DRF permission classes
    │   ├── serializers.py                # DRF serializers for data validation
    │   ├── tasks.py                      # Celery asynchronous tasks (email notifications)
    │   ├── templates
    │   │   └── emails
    │   │       └── booking_confirmation.html  # HTML email template
    │   ├── tests.py
    │   ├── urls.py                       # App-level routing
    │   └── views.py                      # API controllers
    ├── manage.py
    └── requirements.txt                  # Project dependencies

```
## Prerequisites
Before running the project, ensure you have:

### System Requirements
* Python 3.10+
* RabbitMQ installed locally
* MySQL (configured in `.env`)

## Quickstart
1. Create a virtual environment
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
2. Clone the repository
    ```bash
    git clone https://github.com/scottandee/alx_travel_app.git
    cd alx_travel_app/alx_travel_app/
    ```
3. Install dependencies
    ```bash
    pip install -r requirements.txt
    ```
4. Configure environment variables
    ```bash
    cp .env.example .env
    ```
5. Apply migrations
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```
6. Create a user
    ```bash
    python manage.py createsuperuser
    ```
7. Start RabbitMQ:
    ```bash
    sudo service rabbitmq-server start
    ```
8. Start the Celery Worker (Run in a separate terminal):
    ```bash
    celery -A listing worker --loglevel=info
    ```
    You should see:
    ```
    [tasks]
      listings.tasks.send_booking_confirmation_email
    ```
9. Run the development server
    ```bash
    python manage.py runserver
    ```
10. Access Swagger documentation
- Navigate to: http://127.0.0.1:8000/api/swagger/

  ```

## How to Test the Background Email Feature
### Step 1 — Initiate a payment
- **Endpoint**: **POST** `http://127.0.0.1:8000/api/payments/initiate/`
- **Authorization**: Bearer
- **Body**:
  ```json
  {
    "booking": "c0d78ce1-8df7-4e3d-9ff4-ce34f418fc0f"
  }
  ```
- **Success Response**:
  ```json
  {
      "payment_id": "b86cc6d0-b873-4cee-88ee-c27c78cb4464",
      "booking": "216c02a5-ec69-41a4-96e1-97df9f29b45b",
      "tx_ref": "cfba3f32-b8a4-4d7f-97dc-ffc68e4e6388",
      "amount": "1266.00",
      "status": "pending",
      "created_at": "2025-11-09T20:13:32.053487Z",
      "checkout_url": "https://checkout.chapa.co/checkout/payment/yJC9jLGXW4kfhr45DY2tHMemBzEVeKQD0M5EP8cr1fHfS"
  }
  ```
---
### Step 2 — Follow Checkout URL and Pay
Open the checkout url provided in the response of **Step 1** in your browser and pay.

---
### Step 3 — Verify payment
- **Endpoint**: **POST** `http://127.0.0.1:8000/api/payments/verify/{tx_ref}/`
- **Authorization** : Bearer
- **Parameter**: `tx_ref`
- **Success Response**:
  ```json
  {
      "payment_id": "b86cc6d0-b873-4cee-88ee-c27c78cb4464",
      "booking": "216c02a5-ec69-41a4-96e1-97df9f29b45b",
      "tx_ref": "cfba3f32-b8a4-4d7f-97dc-ffc68e4e6388",
      "amount": "1266.00",
      "status": "success",
      "created_at": "2025-11-09T20:13:32.053487Z"
  }

---
### Step 4 — Celery works in the background
Check Celery terminal output:
```
Task listings.tasks.send_booking_confirmation_email succeeded
```
---
## Step 5 — Check Your Email

You will receive:

* A booking confirmation email
* Rendered using the template:
  * `listings/templates/emails/booking_confirmation.html`
