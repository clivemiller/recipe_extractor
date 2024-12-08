from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from extract_recipe import extract_recipe
import os

app = Flask(__name__, static_folder='build', static_url_path='')
CORS(app)

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

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join('build', path)):
        return send_from_directory('build', path)
    else:
        return send_from_directory('build', 'index.html')
    
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))  # Use PORT from environment or default to 5000
    app.run(host='0.0.0.0', port=port)

