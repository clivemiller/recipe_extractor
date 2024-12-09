import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from extract_recipe import extract_recipe

app = Flask(__name__, static_folder='build', static_url_path='')
CORS(app)

#change to render internal?
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://clive_miller:rBFsA6V8EUMkAsmer39Or01qZOZQOHf1@dpg-ctbjttdds78s739ccgd0-a.oregon-postgres.render.com/the_recipe_database')

# Function to get database connection
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

# ------------------ Recipe Extraction API ------------------
@app.route('/extract-recipe', methods=['GET'])
def api_extract_recipe():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    result = extract_recipe(url)
    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "No recipe found or extraction failed"}), 404

# ------------------ User Account APIs ------------------

# Fetch user details
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cur.fetchone()
    conn.close()

    if user:
        return jsonify(user)
    else:
        return jsonify({"error": "User not found"}), 404

# Update user information
@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Validate current password
        cur.execute('SELECT password FROM users WHERE id = %s', (user_id,))
        user = cur.fetchone()
        if not user or not check_password_hash(user['password'], data['currentPassword']):
            return jsonify({"error": "Invalid current password"}), 401

        # Update username or password
        if data.get('newPassword'):
            hashed_password = generate_password_hash(data['newPassword'])
        else:
            hashed_password = user['password']

        cur.execute('''
            UPDATE users
            SET username = %s, password = %s, updated_at = NOW()
            WHERE id = %s
            RETURNING id, username, email, is_paying_member;
        ''', (data['username'], hashed_password, user_id))
        updated_user = cur.fetchone()
        conn.commit()
        return jsonify(updated_user)

    except Exception as e:
        conn.rollback()
        print(f"Error updating user: {e}")
        return jsonify({"error": "Failed to update user"}), 500

    finally:
        conn.close()


# Fetch saved recipes
@app.route('/api/users/<int:user_id>/saved-recipes', methods=['GET'])
def get_saved_recipes(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM saved_recipes WHERE user_id = %s', (user_id,))
    recipes = cur.fetchall()
    conn.close()

    return jsonify(recipes)

# Add a new saved recipe
@app.route('/api/users/<int:user_id>/saved-recipes', methods=['POST'])
def add_saved_recipe(user_id):
    data = request.json  # Ensure you're receiving JSON data

    # Validate data
    if not data or 'recipe_name' not in data or 'recipe_data' not in data:
        return jsonify({"error": "Invalid request data"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Insert the recipe into the saved_recipes table
        cur.execute('''
            INSERT INTO saved_recipes (user_id, recipe_name, recipe_data, created_at, updated_at)
            VALUES (%s, %s, %s, NOW(), NOW())
            RETURNING id, recipe_name, recipe_data;
        ''', (user_id, data['recipe_name'], json.dumps(data['recipe_data'])))
        
        saved_recipe = cur.fetchone()
        conn.commit()
        return jsonify(saved_recipe), 201

    except Exception as e:
        conn.rollback()
        print(f"Error saving recipe: {e}")
        return jsonify({"error": "Failed to save recipe"}), 500

    finally:
        conn.close()

# Delete a saved recipe
@app.route('/api/users/<int:user_id>/saved-recipes/<int:recipe_id>', methods=['DELETE'])
def delete_saved_recipe(user_id, recipe_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('DELETE FROM saved_recipes WHERE id = %s AND user_id = %s RETURNING *;', (recipe_id, user_id))
    deleted_recipe = cur.fetchone()
    conn.commit()
    conn.close()

    if deleted_recipe:
        return jsonify({"message": "Recipe deleted successfully"})
    else:
        return jsonify({"error": "Recipe not found"}), 404
    
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    # Check if email or username already exists
    cur.execute('SELECT * FROM users WHERE email = %s OR username = %s', (email, username))
    existing_user = cur.fetchone()
    if existing_user:
        conn.close()
        return jsonify({"error": "User with this email or username already exists"}), 409

    # Hash the password and save the new user
    hashed_password = generate_password_hash(password)
    cur.execute('''
        INSERT INTO users (username, email, password, created_at, updated_at)
        VALUES (%s, %s, %s, NOW(), NOW())
        RETURNING id, username, email, is_paying_member;
    ''', (username, email, hashed_password))
    new_user = cur.fetchone()
    conn.commit()
    conn.close()

    return jsonify(new_user), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch user by email
    cur.execute('SELECT * FROM users WHERE email = %s', (email,))
    user = cur.fetchone()
    conn.close()

    if not user or not check_password_hash(user['password'], password):
        return jsonify({"error": "Invalid email or password"}), 401

    # Return user details (you can replace this with a JWT or session)
    return jsonify({
        "id": user['id'],
        "username": user['username'],
        "email": user['email'],
        "is_paying_member": user['is_paying_member']
    }), 200


# ------------------ Frontend Serving ------------------
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join('build', path)):
        return send_from_directory('build', path)
    else:
        return send_from_directory('build', 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use PORT from environment or default to 5000
    app.run(host='0.0.0.0', port=port)
