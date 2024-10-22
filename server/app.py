from flask import Flask, request, jsonify
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Database connection details
DB_HOST = 'localhost'
DB_NAME = 'arena'
DB_USER = 'postgres'
DB_PASS = 'Mansi@7038'

def get_db_connection():
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    return conn

# Sign Up Route
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone', None)

    # Hash the password for security
    hashed_password = generate_password_hash(password)

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Insert the user data into the customers table
        cur.execute("""
            INSERT INTO customers (name, email, password, phone)
            VALUES (%s, %s, %s, %s)
        """, (name, email, hashed_password, phone))
        
        conn.commit()
        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400

    finally:
        cur.close()
        conn.close()

# Login Route
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Fetch the user from the database by email
        cur.execute("""
            SELECT id, password FROM customers WHERE email = %s
        """, (email,))
        
        user = cur.fetchone()

        if user is None:
            return jsonify({"error": "User not found"}), 404

        user_id, hashed_password = user

        # Check if the password is correct
        if not check_password_hash(hashed_password, password):
            return jsonify({"error": "Invalid password"}), 401

        # If login is successful, you can return a token or success message
        return jsonify({"message": "Login successful", "user_id": user_id}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
