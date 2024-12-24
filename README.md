# Event Reservations API

This is a Flask-based API for managing event reservations, including users, customers, events, venues, and seat bookings. The API uses MySQL as the database and JWT for authentication.

## Requirements

- Python 3.x
- Flask
- Flask-MySQLdb
- Flask-HTTPAuth
- PyJWT
- Werkzeug

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/lesterbal/event_reservations_api
    cd event_reservations_api
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

4. Configure the MySQL database in [app_revision.py](http://_vscodecontentref_/0):
    ```python
    app.config["MYSQL_HOST"] = "your_mysql_host"
    app.config["MYSQL_USER"] = "your_mysql_user"
    app.config["MYSQL_PASSWORD"] = "your_mysql_password"
    app.config["MYSQL_DB"] = "your_database_name"
    app.config["SECRET_KEY"] = "your_secret_key"
    ```

5. Run the application:
    ```sh
    python app_revision.py
    ```

## API Endpoints

### Authentication

- **Login**
    - `POST /login`
    - Request Body:
        ```json
        {
            "username": "your_username",
            "password": "your_password"
        }
        ```
    - Response:
        ```json
        {
            "success": true,
            "message": "Logged In Successfully",
            "token": "your_jwt_token",
            "data": {
                "username": "your_username",
                "role_id": 1
            }
        }
        ```

- **Register**
    - `POST /register`
    - Request Body:
        ```json
        {
            "username": "new_username",
            "password": "new_password"
        }
        ```
    - Response:
        ```json
        {
            "success": true,
            "message": "Account created successfully"
        }
        ```

### Users

- **Get Users**
    - `GET /users`
    - Response:
        ```json
        [
            {
                "user_id": 1,
                "username": "user1",
                "passwd": "hashed_password",
                "token_id": "jwt_token",
                "role_id": 1
            },
            ...
        ]
        ```

### Customers

- **Get All Customers**
    - `GET /customers`
    - Response:
        ```json
        [
            {
                "customer_id": 1,
                "payment_method": "Credit Card",
                "customer_name": "John Doe",
                "customer_phone": "1234567890",
                "customer_email": "john@example.com",
                "customer_address": "123 Main St",
                "customer_payment_method_details": "Visa"
            },
            ...
        ]
        ```

- **Get Customer by ID**
    - `GET /customers/<int:customer_id>`
    - Response:
        ```json
        {
            "customer_id": 1,
            "payment_method": "Credit Card",
            "customer_name": "John Doe",
            "customer_phone": "1234567890",
            "customer_email": "john@example.com",
            "customer_address": "123 Main St",
            "customer_payment_method_details": "Visa"
        }
        ```

- **Create Customer**
    - `POST /customers`
    - Request Body:
        ```json
        {
            "payment_method": "Credit Card",
            "customer_name": "John Doe",
            "customer_phone": "1234567890",
            "customer_email": "john@example.com",
            "customer_address": "123 Main St",
            "customer_payment_method_details": "Visa"
        }
        ```
    - Response:
        ```json
        {
            "success": true,
            "message": "Customer created successfully"
        }
        ```

- **Update Customer**
    - `PUT /customers/<int:customer_id>`
    - Request Body:
        ```json
        {
            "payment_method": "Credit Card",
            "customer_name": "John Doe",
            "customer_phone": "1234567890",
            "customer_email": "john@example.com",
            "customer_address": "123 Main St",
            "customer_payment_method_details": "Visa"
        }
        ```
    - Response:
        ```json
        {
            "success": true,
            "message": "Customer updated successfully"
        }
        ```

- **Delete Customer**
    - `DELETE /customers/<int:customer_id>`
    - Response:
        ```json
        {
            "success": true,
            "message": "Customer deleted successfully"
        }
        ```

### Events

- **Get All Events**
    - `GET /events`
    - Response:
        ```json
        [
            {
                "event_id": 1,
                "event_type": "Concert",
                "venue_id": 1,
                "event_name": "Rock Concert",
                "event_start_date": "2023-12-01T18:00:00",
                "event_end_date": "2023-12-01T21:00:00"
            },
            ...
        ]
        ```

- **Get Event by ID**
    - `GET /events/<int:event_id>`
    - Response:
        ```json
        {
            "event_id": 1,
            "event_type": "Concert",
            "venue_id": 1,
            "event_name": "Rock Concert",
            "event_start_date": "2023-12-01T18:00:00",
            "event_end_date": "2023-12-01T21:00:00"
        }
        ```

- **Create Event**
    - `POST /events`
    - Request Body:
        ```json
        {
            "event_type": "Concert",
            "venue_id": 1,
            "event_name": "Rock Concert",
            "event_start_date": "2023-12-01T18:00:00",
            "event_end_date": "2023-12-01T21:00:00"
        }
        ```
    - Response:
        ```json
        {
            "success": true,
            "message": "Event created successfully"
        }
        ```

- **Update Event**
    - `PUT /events/<int:event_id>`
    - Request Body:
        ```json
        {
            "event_type": "Concert",
            "venue_id": 1,
            "event_name": "Rock Concert",
            "event_start_date": "2023-12-01T18:00:00",
            "event_end_date": "2023-12-01T21:00:00"
        }
        ```
    - Response:
        ```json
        {
            "success": true,
            "message": "Event updated successfully"
        }
        ```

- **Delete Event**
    - `DELETE /events/<int:event_id>`
    - Response:
        ```json
        {
            "success": true,
            "message": "Event deleted successfully"
        }
        ```

### Seat Bookings

- **Get All Seat Bookings**
    - `GET /seat_bookings`
    - Response:
        ```json
        [
            {
                "seat_booking_id": 1,
                "booking_id": 1,
                "seat_booking_datetime": "2023-12-01T18:00:00",
                "venue_row_number": 5,
                "seat_number": "A1"
            },
            ...
        ]
        ```

- **Get Seat Booking by ID**
    - `GET /seat_bookings/<int:seat_booking_id>`
    - Response:
        ```json
        {
            "seat_booking_id": 1,
            "booking_id": 1,
            "seat_booking_datetime": "2023-12-01T18:00:00",
            "venue_row_number": 5,
            "seat_number": "A1"
        }
        ```

- **Create Seat Booking**
    - `POST /seat_bookings`
    - Request Body:
        ```json
        {
            "booking_id": 1,
            "seat_number": "A1",
            "seat_booking_datetime": "2023-12-01T18:00:00",
            "venue_row_number": 5
        }
        ```
    - Response:
        ```json
        {
            "success": true,
            "message": "Seat booking created successfully"
        }
        ```

- **Update Seat Booking**
    - `PUT /seat_bookings/<int:seat_booking_id>`
    - Request Body:
        ```json
        {
            "booking_id": 1,
            "seat_number": "A2",
            "seat_booking_datetime": "2023-12-01T19:00:00",
            "venue_row_number": 6
        }
        ```
    - Response:
        ```json
        {
            "success": true,
            "message": "Seat booking updated successfully"
        }
        ```

- **Delete Seat Booking**
    - `DELETE /seat_bookings/<int:seat_booking_id>`
    - Response:
        ```json
        {
            "success": true,
            "message": "Seat booking deleted successfully"
        }
        ```
