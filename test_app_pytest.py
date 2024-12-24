import pytest, json, random, requests
from app import app, mysql
import faker, os, datetime
os.system("cls" if os.name == "nt" else "clear")

# INIT
print("The test will take a while to run, please wait...")
fake = faker.Faker()
username = fake.user_name()
password = fake.password()

real_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Imxlc3RlciIsImV4cCI6MTczNTAxMzgxM30.cCoK7yL8KcKK6wl607VTkb9TLECTT4rRMxX0rUpXHI0'
def apply_token(token): global real_token ; real_token = token
def get_token(): global real_token ; return real_token
evenet_types_sample = ["Concert", "Theatre", "Sports", "Comedy", "Dance", 
                        "Musical", "Magic", "Circus", "Opera", "Ballet", 
                        "Film", "Exhibition", "Festival", "Conference", 
                        "Seminar", "Workshop", "Class", "Course", "Lecture", 
                        "Talk", "Tour", "Party", "Gala", "Ball", "Prom", 
                        "Wedding", "Reception", "Dinner", "Lunch", "Brunch", 
                        "Breakfast", "Picnic", "BBQ", "Banquet", "Buffet", 
                        "Cocktail", "Reception", "Gathering", "Meeting", 
                        "Rally", "Protest", "March", "Parade", "Demonstration", 
                        "Celebration", "Fiesta", "Fete", "Carnival", "Fair", 
                        "Show", "Expo", "Market", "Flea Market", "Swap Meet", 
                        "Car Boot Sale", "Yard Sale", "Garage Sale", "Estate Sale", 
                        "Auction", "Raffle", "Lottery", "Draw", "Competition", "Contest", "Tournament"]
data_customers = {}
data_venues = {}
data_events = {}
data_customer_bookings = {}
data_seat_bookings = {}

DEBUG_VERBOSE = True

# Requests function
host = "http://localhost:5000"
def refresh_customers():
    try: return requests.get(f"{host}/customers")
    except IndexError: print("No customers found") ; return None
def refresh_events():
    try: return requests.get(f"{host}/events")
    except IndexError:
        print("No events found")
        return {
            "event_id" : 192,
            "event_type" : "Concert",
            "venue_id" : 3,
            "event_name" : "The Best Concert",
            "event_start_date" : "2024-12-31 23:59:59",
            "event_end_date" : "2024-12-31 23:59:59",
        }
    
def refresh_venues():
    try: return requests.get(f"{host}/venues")
    except IndexError:
        print("No venues found")
        return {
            "venue_id" : 192,
            "venue_name" : "The Best Venue",
            "venue_seat_capacity" : 1000
        }
def refresh_customer_bookings():    
    try: return requests.get(f"{host}/customer_bookings")
    except IndexError:
        print("No customer bookings found")
        return {
            "booking_id" : 192,
            "customer_id" : 3,
            "event_id" : 3,
            "" : "2024-12-31 23:59:59",

        }
def refresh_seat_bookings():
    try: return requests.get(f"{host}/seat_bookings")
    except IndexError:
        print("No seat bookings found")
        return {
            "booking_id" : 192,
            "seat_booking_datetime" : "2024-12-31 23:59:59",
            "venue_row_number" : 1,
            "seat_number" : 1,
        }

R_CUSTOMERS = refresh_customers()
R_EVENTS = refresh_events()
R_VENUES = refresh_venues()
R_CUSTOMER_BOOKINGS = refresh_customer_bookings()
R_SEAT_BOOKINGS = refresh_seat_bookings()

LAST_CUSTOMER_ID = R_CUSTOMERS.json()[-1]["customer_id"] if R_CUSTOMERS.json()[-1]["customer_id"] else 192
LAST_EVENT_ID = R_EVENTS.json()[-1]["event_id"] if R_EVENTS.json()[-1]["event_id"] else 192
LAST_VENUE_ID = R_VENUES.json()[-1]["venue_id"] if R_VENUES.json()[-1]["venue_id"] else 192
LAST_CUSTOMER_BOOKING_ID = R_CUSTOMER_BOOKINGS.json()[-1]["booking_id"] if R_CUSTOMER_BOOKINGS.json()[-1]["booking_id"] else 192
LAST_SEAT_BOOKING_ID = R_SEAT_BOOKINGS.json()[-1]["seat_booking_id"] if R_SEAT_BOOKINGS.json()[-1]["seat_booking_id"] else 192
    
# Generator functions
def gen_event():
    global data_events
    data_events = {
        "event_type" : random.choice(evenet_types_sample),
        "venue_id" : 3,
        "event_name" : fake.catch_phrase(),
        "event_start_date" : fake.date_time_this_year(),
        "event_end_date" : fake.date_time_this_year(),
    }
    return data_events

def gen_customer():
    data_customers = {
        "payment_method" : "Credit Card",
        "customer_name" : fake.name(),
        "customer_email" : fake.email(),
        "customer_phone" : fake.phone_number(),
        "customer_address" : "Address Street, Sam sam City, 12345 " + fake.zipcode(),
        "customer_city" : fake.city(),
        "customer_payment_method_details" : fake.credit_card_number(),
    }
    if DEBUG_VERBOSE: print(data_customers)
    return data_customers

def gen_venue():
    data_venues = {
        "venue_name" : fake.company(),
        "venue_seat_capacity" : fake.random_int(min=100, max=1000, step=50)
    }
    return data_venues

def gen_customer_booking():
    data_customer_bookings = {
        "customer_id" : 3,
        "event_id" : 3,
        "event_date_time" : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return data_customer_bookings

def gen_seat_booking():
    data_seat_bookings = {
        "booking_id" : LAST_CUSTOMER_BOOKING_ID,
        "customer_id" : LAST_CUSTOMER_ID,
        "event_id" : LAST_EVENT_ID,
        "event_datetime" : fake.date_time_this_year(),
        "booking_made_date" : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return data_seat_bookings

def gen_seat_booking():
    data_seat_bookings = {
        "booking_id" : LAST_CUSTOMER_BOOKING_ID,
        "seat_booking_datetime" : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "venue_row_number" : fake.random_int(min=1, max=100, step=1),
        "seat_number" : fake.random_int(min=1, max=100, step=1),
    }
    return data_seat_bookings


# Start program

@pytest.fixture

def mock_db(mocker):
    mock_conn = mocker.patch('flask_mysqldb.MySQL.connection')
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_cursor

def test_index():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert response.data == b"Hello :)" in response.data

# First register
def test_register_first():
    client = app.test_client()
    response = client.post('/register', json={
        'username': username,
        'password': password
    })
    assert response.status_code == 201
    assert response.json['success'] == True

# Duplicate register
def test_register_second():
    client = app.test_client()
    response = client.post('/register', json={
        'username': username,
        'password': password
    })
    assert response.status_code == 409
    assert response.json['success'] == False

# Login error
def test_login_error():
    client = app.test_client()
    response = client.post('/login', json={
        'username': username,
        'password': fake.password()
    })
    assert response.status_code == 401
    assert response.json['success'] == False

def test_login():
    global real_token
    client = app.test_client()
    response = client.post('/login', json={
        'username': username,
        'password': password
    })
    assert response.status_code == 200
    data = json.loads(response.data.decode())
    real_token = apply_token(data.get('token'))
    assert 'token' in data
# real_token = test_login()


# CUSTOMERS
def test_get_customers():
    client = app.test_client()
    response = client.get('/customers')
    assert response.status_code == 200
    assert len(response.json) >= 0

def test_get_customer_id_success():
    client = app.test_client()
    response = client.get(f'/customers/{LAST_CUSTOMER_ID}')
    assert response.status_code == 200
    assert len(response.json) >= 0

def test_customer_id_not_found():
    client = app.test_client()
    response = client.get(f'/customers/9999')
    assert response.status_code == 404

def test_post_customers_success():
    client = app.test_client()
    # Login to get the token
    response = client.post('/login', json={
        'username': username,
        'password': password
    }, headers={'Content-Type': 'application/json'})
    
    # assert response.status_code == 200
    token = json.loads(response.get_data(as_text=True)).get('token')
    
    # Use the token to make an authorized request
    response = client.post('/customers', json=gen_customer(), headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    })
    
    if response.status_code != 201:
        print(f"Error: {response.status_code}, {response.get_data(as_text=True)}")
    assert response.status_code == 201

# def test_post_customers_fail():
#     client = app.test_client()
#     # Refresh to get latest customer id
#     R_CUSTOMERS = refresh_customers()
#     LAST_CUSTOMER_ID = R_CUSTOMERS.json()[-1]["customer_id"]
#     response = client.post('/customers', data=json.dumps(gen_customer()), headers={
#         'Authorization': f'Bearer {real_token}',
#         'Content-Type': 'application/json'
#     })
#     assert response.status_code == 409

# def test_put_customers_success():
#     client = app.test_client()
#     response = client.put(f'/customers/{LAST_CUSTOMER_ID+1}', json=gen_customer(), headers={
#         'Authorization': f'Bearer {real_token}',
#         'Content-Type': 'application/json'
#     })
#     if response.status_code != 200:
#         print(f"Error: {response.status_code}, {response.data.decode()}")
#     assert response.status_code == 200

# def test_delete_customers_success():
#     client = app.test_client()
#     response = client.delete(f'/customers/{LAST_CUSTOMER_ID+1}', headers={
#         'Authorization': f'Bearer {real_token}'
#     })
#     if response.status_code != 200:
#         print(f"Error: {response.status_code}, {response.data.decode()}")
#     assert response.status_code == 200

# def test_get_venues():
#     client = app.test_client()
#     response = client.get('/venues')
#     assert response.status_code == 200
#     assert len(response.json) >= 0

if __name__ == "__main__":
    pytest.main()