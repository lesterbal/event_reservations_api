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
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Token is missing"}), 401
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

@app.route("/customers", methods=["GET", "POST", "PUT", "DELETE"])
def customers(get_customer_id=None):
    table_name = "customers"

    cur = mysql.connection.cursor()

    # GET all customers or specific customer
    if request.method == "GET":
        
        # Fetch customer
        if customer_id:
            cur.execute(f"SELECT * FROM {table_name} WHERE customer_id = %s", (customer_id,))
            customer = cur.fetchone()
            if not customer:
                return jsonify({"success": False, "message": "Customer not found"}), 404
                customer_data = {
                    "customer_id": customer[0],
                    "payment_method": customer[1],
                    "customer_name": customer[2],
                    "customer_phone": customer[3],
                    "customer_email": customer[4],
                    "customer_address": customer[5]
                }
                return jsonify(customer_data), 200
            else:
                cur.execute(f"SELECT * FROM {table_name}")
                customers = cur.fetchall()
                customer_list = []
                for customer in customers:
                    customer_list.append({
                        "customer_id": customer[0],
                        "payment_method": customer[1],
                        "customer_name": customer[2],
                        "customer_phone": customer[3],
                        "customer_email": customer[4],
                        "customer_address": customer[5]
                    })
                return jsonify(customer_list), 200

    # CREATE new customer
    elif request.method == "POST":
        data = request.get_json()
        payment_method = data.get("payment_method")
        customer_name = data.get("customer_name")
        customer_phone = data.get("customer_phone")
        customer_email = data.get("customer_email")
        customer_address = data.get("customer_address")

        if not all([payment_method, customer_name, customer_phone, customer_email, customer_address]):
            return jsonify({"success": False, "message": "All fields are required"}), 400

        try:
            cur.execute(f"INSERT INTO {table_name} (payment_method, customer_name, customer_phone, customer_email, customer_address) VALUES (%s, %s, %s, %s, %s)",
                        (payment_method, customer_name, customer_phone, customer_email, customer_address))
            mysql.connection.commit()
            return jsonify({"success": True, "message": "Customer created successfully"}), 201
        except Exception as e:
            mysql.connection.rollback()
            return jsonify({"success": False, "message": str(e)}), 500

    # UPDATE existing customer
    elif request.method == "PUT":
        data = request.get_json()
        payment_method = data.get("payment_method")
        customer_name = data.get("customer_name")
        customer_phone = data.get("customer_phone")
        customer_email = data.get("customer_email")
        customer_address = data.get("customer_address")

        if not all([payment_method, customer_name, customer_phone, customer_email, customer_address]):
            return jsonify({"success": False, "message": "All fields are required"}), 400

        cur.execute(f"SELECT * FROM {table_name} WHERE customer_id = %s", (customer_id,))
        if not cur.fetchone():
            return jsonify({"success": False, "message": "Customer not found"}), 404

        try:
            cur.execute(f"UPDATE {table_name} SET payment_method = %s, customer_name = %s, customer_phone = %s, customer_email = %s, customer_address = %s WHERE customer_id = %s",
                        (payment_method, customer_name, customer_phone, customer_email, customer_address, customer_id))
            mysql.connection.commit()
            return jsonify({"success": True, "message": "Customer updated successfully"}), 200
        except Exception as e:
            mysql.connection.rollback()
            return jsonify({"success": False, "message": str(e)}), 500

    # DELETE customer
    elif request.method == "DELETE":
        cur.execute(f"SELECT * FROM {table_name} WHERE customer_id = %s", (customer_id,))
        if not cur.fetchone():
            return jsonify({"success": False, "message": "Customer not found"}), 404

        try:
            cur.execute(f"DELETE FROM {table_name} WHERE customer_id = %s", (customer_id,))
            mysql.connection.commit()
            return jsonify({"success": True, "message": "Customer deleted successfully"}), 200
        except Exception as e:
            mysql.connection.rollback()
            return jsonify({"success": False, "message": str(e)}), 500

    else:
        return jsonify({"success": False, "message": "Method not allowed"}), 405


if __name__ == "__main__":
    app.run(debug=True)

