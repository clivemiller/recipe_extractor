import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from extract_recipe import extract_recipe
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='build', static_url_path='')
CORS(app)

# Change to render internal?
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
        if not user or not check_password_hash(user['password'], data.get('currentPassword', '')):
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
        ''', (data.get('username', user['username']), hashed_password, user_id))
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
    if not data or 'recipe_name' not in data or 'recipe_data' not in data or 'tab_name' not in data:
        return jsonify({"error": "Invalid request data. 'recipe_name', 'recipe_data', and 'tab_name' are required."}), 400

    tab_name = data['tab_name']

    # Validate that the tab_name exists for the user
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('SELECT tab_names FROM users WHERE id = %s', (user_id,))
        user = cur.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404

        user_tabs = user['tab_names'] if user['tab_names'] else []
        if tab_name not in user_tabs:
            return jsonify({"error": f"Tab '{tab_name}' does not exist for the user."}), 400

    except Exception as e:
        print(f"Error validating tab name: {e}")
        return jsonify({"error": "Failed to validate tab name"}), 500
    finally:
        conn.close()

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Check for duplicates
        cur.execute('''
            SELECT * FROM saved_recipes 
            WHERE user_id = %s AND recipe_name = %s
        ''', (user_id, data['recipe_name']))
        existing_recipe = cur.fetchone()
        if existing_recipe:
            return jsonify({"error": "Recipe with this name already exists"}), 409

        # Insert the recipe into the saved_recipes table with tab_name
        cur.execute('''
            INSERT INTO saved_recipes (user_id, recipe_name, recipe_data, tab_name, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
            RETURNING id, recipe_name, recipe_data, tab_name;
        ''', (user_id, data['recipe_name'], json.dumps(data['recipe_data']), tab_name))
        
        saved_recipe = cur.fetchone()
        conn.commit()
        return jsonify(saved_recipe), 201

    except Exception as e:
        conn.rollback()
        print(f"Error saving recipe: {e}")
        return jsonify({"error": "Failed to save recipe"}), 500

    finally:
        conn.close()

# Bulk update recipes to a specific tab
@app.route('/api/users/<int:user_id>/saved-recipes/move-to-tab', methods=['PUT'])
def move_recipes_to_tab(user_id):
    data = request.json

    if not data or 'source_tab' not in data or 'target_tab' not in data:
        return jsonify({"error": "Invalid request data. 'source_tab' and 'target_tab' are required."}), 400

    source_tab = data['source_tab']
    target_tab = data['target_tab']

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Validate user exists
        cur.execute('SELECT tab_names FROM users WHERE id = %s', (user_id,))
        user = cur.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404

        user_tabs = user['tab_names'] if user['tab_names'] else []
        if target_tab != 'General' and target_tab not in user_tabs:
            return jsonify({"error": f"Tab '{target_tab}' does not exist for the user."}), 400

        # Update multiple recipes
        cur.execute('''
            UPDATE saved_recipes
            SET tab_name = %s, updated_at = NOW()
            WHERE user_id = %s AND tab_name = %s
            RETURNING id, recipe_name, recipe_data, tab_name;
        ''', (target_tab, user_id, source_tab))

        updated_recipes = cur.fetchall()

        if not updated_recipes:
            return jsonify({"message": "No recipes found to update."}), 200

        conn.commit()
        return jsonify({"updated_recipes": updated_recipes}), 200

    except Exception as e:
        conn.rollback()
        print(f"Error moving recipes to tab: {e}")
        return jsonify({"error": "Failed to move recipes to tab"}), 500

    finally:
        conn.close()

# Update the tab_name of a saved recipe
@app.route('/api/users/<int:user_id>/saved-recipes/<int:recipe_id>/tab', methods=['PUT'])
def update_saved_recipe_tab(user_id, recipe_id):
    data = request.json

    if not data or 'tab_name' not in data:
        return jsonify({"error": "Invalid request data. 'tab_name' is required."}), 400

    new_tab_name = data['tab_name']

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Validate that the new_tab_name exists for the user
        cur.execute('SELECT tab_names FROM users WHERE id = %s', (user_id,))
        user = cur.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404

        user_tabs = user['tab_names'] if user['tab_names'] else []
        if new_tab_name not in user_tabs:
            return jsonify({"error": f"Tab '{new_tab_name}' does not exist for the user."}), 400

        # Update the tab_name of the saved recipe
        cur.execute('''
            UPDATE saved_recipes
            SET tab_name = %s, updated_at = NOW()
            WHERE id = %s AND user_id = %s
            RETURNING id, recipe_name, recipe_data, tab_name;
        ''', (new_tab_name, recipe_id, user_id))
        
        updated_recipe = cur.fetchone()
        if not updated_recipe:
            return jsonify({"error": "Recipe not found"}), 404

        conn.commit()
        return jsonify(updated_recipe), 200

    except Exception as e:
        conn.rollback()
        print(f"Error updating recipe tab: {e}")
        return jsonify({"error": "Failed to update recipe tab"}), 500

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

# Tabs
@app.route('/api/users/<int:user_id>/tabs', methods=['GET'])
def get_tabs(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT tab_names FROM users WHERE id = %s', (user_id,))
    user = cur.fetchone()
    conn.close()

    if user and user['tab_names']:
        return jsonify(user['tab_names'])
    return jsonify([])

@app.route('/api/users/<int:user_id>/tabs', methods=['POST'])
def add_tab(user_id):
    data = request.json
    new_tab = data.get('tab_name')

    if not new_tab:
        return jsonify({"error": "Tab name is required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute('SELECT tab_names FROM users WHERE id = %s', (user_id,))
        user = cur.fetchone()
        tabs = user['tab_names'] if user['tab_names'] else []

        if new_tab in tabs:
            return jsonify({"error": "Tab already exists"}), 409

        tabs.append(new_tab)
        cur.execute('UPDATE users SET tab_names = %s WHERE id = %s', (json.dumps(tabs), user_id))
        conn.commit()
        return jsonify({"message": "Tab added successfully"}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Failed to add tab"}), 500

    finally:
        conn.close()

@app.route('/api/users/<int:user_id>/tabs/<string:tab_name>', methods=['DELETE'])
def delete_tab(user_id, tab_name):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute('SELECT tab_names FROM users WHERE id = %s', (user_id,))
        user = cur.fetchone()
        tabs = user['tab_names'] if user['tab_names'] else []

        if tab_name not in tabs:
            return jsonify({"error": "Tab not found"}), 404

        tabs.remove(tab_name)
        cur.execute('UPDATE users SET tab_names = %s WHERE id = %s', (json.dumps(tabs), user_id))
        conn.commit()
        return jsonify({"message": "Tab deleted successfully"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Failed to delete tab"}), 500

    finally:
        conn.close()

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
