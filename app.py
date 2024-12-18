from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_httpauth import HTTPBasicAuth
import jwt, datetime , json
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# PROGRAM:: REQUIREMENTS 

app = Flask(__name__)

app.config["MYSQL_HOST"] = "192.168.1.140"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "event"
app.config["SECRET_KEY"] = "lesterbal"

mysql = MySQL(app)
auth = HTTPBasicAuth()

def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            return jsonify({"error": "Token is missing"}), 401
        
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Invalid token format"}), 401
        
        token = auth_header.replace("Bearer ", "")
        
        try:
            decoded_token = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            request.username = decoded_token["username"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired!, login again!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        return f(*args, **kwargs)
    return wrapper
    
@app.errorhandler(404)
def page_not_found(e):
    return "NOT FOUND :P", 404

@app.route("/users", methods=["GET"])
@token_required
def get_users():
    table_name = "users"
    query = f"SELECT * FROM {table_name}"

    cur = mysql.connection.cursor()

    cur.execute(query)
    entries = cur.fetchall()

    users = []

    for entry in entries:
        user = {
            'user_id': entry[0],
            'username': entry[1],
            'passwd': entry[2],
            'token_id': entry[3],
            'role_id': entry[4]
        }
        users.append(user)
    return jsonify(users), 200

# Homepage
@app.route("/", methods=["GET"])
def hello_world():
    return "Hello :)"

# SECTION: LOGIN DATA
@app.route("/login", methods=["POST","GET"])
def login_post():

    if request.method == "GET":
        return jsonify({"message": "You need to query it :P"}), 200

    elif request.method == "POST":
        
        # curl -X POST localhost:5000/login -H "Content-Type: application/json" -d "{\"username\":\"your_username\",\"password\":\"your_password\"}"
        # curl -X POST http://localhost:5000/login -H "Content-Type: application/json" -d '{"username":"your_username","password":"your_password"}'

        data = request.json

        # Fetch username and password
        # Validate input
        username = data.get("username")
        password = data.get("password")

        # Validate input
        if not username or not password:
            return jsonify({"success": False, "message": "Username and Password Required"}), 400

        # Query user data
        cur = mysql.connection.cursor()
        cur.execute("""SELECT 
                            username,
                            passwd,
                            role_id
                        FROM users 
                        WHERE username = %s""",
                        (username,))

        user_auth = cur.fetchone()

        # Check authentication
        if user_auth and check_password_hash(user_auth[1], password):
            
            token = jwt.encode({
                "username": username,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }, app.config["SECRET_KEY"], algorithm="HS256")
            
            cur.execute("""UPDATE users
                        SET token_id = %s
                        WHERE username = %s""",
                        (token, username))
            
            mysql.connection.commit()

            return jsonify({
                "success": True,
                "message": "Logged In Successfully",
                "token": token,
                "data": user_auth
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Invalid Username or Password"
            }), 401


# SECTION: CREATE AN USER ACCOUNT
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        # curl -X GET http://localhost:5000/users
        return jsonify({"message": "You need to query it :P"}), 200

    elif request.method == "POST":
        # curl -X POST -H "Content-Type: application/json" -d '{"username": "lester", "password": "lester", "role_id": "1"}' http://localhost:5000/register
        data = request.json
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"success": False, "message": "Username and password are required"}), 401

        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT username FROM users WHERE username = %s", (username,))
            
            if cur.fetchone():
                return jsonify({"success": False, "message": "Username already exists"}), 409

            role_id = 1  # Default role_id
            password_enc = generate_password_hash(password)
            
            cur.execute("INSERT INTO users (username, passwd, role_id) VALUES (%s, %s, %s)", (username, password_enc, role_id))
            mysql.connection.commit()
            
            return jsonify({"success": True, "message": "Account created successfully"}), 201
        
        except Exception as e:
            mysql.connection.rollback()
            return jsonify({"success": False, "message": str(e)}), 409
        finally:
            cur.close()

    @app.route("/users", methods=["GET", "POST"])
    def users(user_id=None):
        table_name = "users"
        cur = mysql.connection.cursor()
        if request.method == "GET":
            cur.execute(f"SELECT * FROM {table_name}")
            entries = cur.fetchall()

            users = []
            for entry in entries:
                user = {
                    'user_id': entry[0],
                    'username': entry[1],
                    'passwd': entry[2],
                    'token_id': entry[3],
                    'role_id': entry[4]
                }
                users.append(user)
            return jsonify(users), 200

@app.route("/customers", methods=["GET", "POST"])
@app.route("/customers/<int:customer_id>", methods=["GET", "PUT", "DELETE"])
def customers(customer_id=None):
    table_name = "customers"
    cur = mysql.connection.cursor()

    # Helper function
    def get_customer(customer_id):
        cur.execute(f"SELECT * FROM {table_name} WHERE customer_id = %s", (customer_id,))
        customer = cur.fetchone()
        if not customer:
            return None
        return {
            "customer_id": customer[0],
            "payment_method": customer[1],
            "customer_name": customer[2],
            "customer_phone": customer[3],
            "customer_email": customer[4],
            "customer_address": customer[5]
        }

    # GET all customers or specific customer
    if request.method == "GET":
        if customer_id:
            customer = get_customer(customer_id)
            if not customer:
                return jsonify({"success": False, "message": "Customer not found"}), 404
            return jsonify(customer)
        else:
            cur.execute(f"SELECT * FROM {table_name}")
            customers = cur.fetchall()
            customer_list = [get_customer(customer[0]) for customer in customers]
            return jsonify(customer_list)

    # CREATE new customer
    @token_required
    def create_customer():
        if request.method == "POST":
            data = request.get_json()
            try:
                cur.execute(f"INSERT INTO {table_name} (payment_method, customer_name, customer_phone, customer_email, customer_address) VALUES (%s, %s, %s, %s, %s)",
                            (data["payment_method"], data["customer_name"], data["customer_phone"], data["customer_email"], data["customer_address"]))
                mysql.connection.commit()
                return jsonify({"success": True, "message": "Customer created successfully"})
            except Exception as e:
                mysql.connection.rollback()
                return jsonify({"success": False, "message": str(e)})

    # UPDATE existing customer
    @token_required
    def update_customer():
        if request.method == "PUT":
            data = request.get_json()
            customer = get_customer(customer_id)
            if not customer:
                return jsonify({"success": False, "message": "Customer not found"}), 404
            try:
                cur.execute(f"UPDATE {table_name} SET payment_method = %s, customer_name = %s, customer_phone = %s, customer_email = %s, customer_address = %s WHERE customer_id = %s",
                            (data["payment_method"], data["customer_name"], data["customer_phone"], data["customer_email"], data["customer_address"], customer_id))
                mysql.connection.commit()
                return jsonify({"success": True, "message": "Customer updated successfully"})
            except Exception as e:
                mysql.connection.rollback()
                return jsonify({"success": False, "message": str(e)})

    # DELETE customer
    @token_required
    def delete_customer():
        if request.method == "DELETE":
            customer = get_customer(customer_id)
            if not customer:
                return jsonify({"success": False, "message": "Customer not found"}), 404
            try:
                cur.execute(f"DELETE FROM {table_name} WHERE customer_id = %s", (customer_id,))
                mysql.connection.commit()
                return jsonify({"success": True, "message": "Customer deleted successfully"})
            except Exception as e:
                mysql.connection.rollback()
                return jsonify({"success": False, "message": str(e)})

    # Call functions
    if request.method == "POST":
        return create_customer()
    elif request.method == "PUT":
        return update_customer()
    elif request.method == "DELETE":
        return delete_customer()
    else:
        return jsonify({"success": False, "message": "Method not allowed"}), 405


# Event
@app.route("/events", methods=["GET", "POST"])
@app.route("/events/<int:event_id>", methods=["GET", "PUT", "DELETE"])
def events(event_id=None):
    table_name = "events"
    cur = mysql.connection.cursor()

    # Helper function
    def get_event(event_id):
        cur.execute(f"SELECT * FROM {table_name} WHERE event_id = %s", (event_id,))
        event = cur.fetchone()
        if not event:
            return None
        return {
            "event_id": event[0],
            "event_type": event[1],
            "venue_name": event[2],
            "event_name": event[3],
            "event_start_date": event[4],
            "event_end_date": event[5]
        }

    # GET all events or specific event
    if request.method == "GET":
        if event_id:
            event = get_event(event_id)
            if not event:
                return jsonify({"success": False, "message": "Event not found"}), 404
            return jsonify(event)
        else:
            cur.execute(f"SELECT * FROM {table_name}")
            events = cur.fetchall()
            event_list = [get_event(event[0]) for event in events]
            return jsonify(event_list)

    # CREATE new event
    @token_required
    def create_event():
        if request.method == "POST":
            data = request.get_json()
            try:
                cur.execute(f"INSERT INTO {table_name} (event_type, venue_name, event_name, event_start_date, event_end_date) VALUES (%s, %s, %s, %s, %s)",
                            (data["event_type"], data["venue_name"], data["event_name"], data["event_start_date"], data["event_end_date"]))
                mysql.connection.commit()
                return jsonify({"success": True, "message": "Event created successfully"})
            except Exception as e:
                mysql.connection.rollback()
                return jsonify({"success": False, "message": "Missing your query"})

    # UPDATE existing event
    @token_required
    def update_event():
        if request.method == "PUT":
            data = request.get_json()
            event = get_event(event_id)
            if not event:
                return jsonify({"success": False, "message": "Event not found"}), 404
            try:
                cur.execute(f"UPDATE {table_name} SET event_type = %s, venue_name = %s, event_name = %s, event_start_date = %s, event_end_date = %s WHERE event_id = %s",
                            (data["event_type"], data["venue_name"], data["event_name"], data["event_start_date"], data["event_end_date"], event_id))
                mysql.connection.commit()
                return jsonify({"success": True, "message": "Event updated successfully"})
            except Exception as e:
                mysql.connection.rollback()
                return jsonify({"success": False, "message": str(e)})

    # DELETE event
    @token_required
    def delete_event():
        if request.method == "DELETE":
            event = get_event(event_id)
            if not event:
                return jsonify({"success": False, "message": "Event not found"}), 404
            try:
                cur.execute(f"DELETE FROM {table_name} WHERE event_id = %s", (event_id,))
                mysql.connection.commit()
                return jsonify({"success": True, "message": "Event deleted successfully"})
            except Exception as e:
                mysql.connection.rollback()
                return jsonify({"success": False, "message": str(e)})

    # Call functions
    if request.method == "POST":
        return create_event()
    elif request.method == "PUT":
        return update_event()
    elif request.method == "DELETE":
        return delete_event()
    else:
        return jsonify({"success": False, "message": "Method not allowed"}), 405


if __name__ == "__main__":
    app.run(debug=True)

