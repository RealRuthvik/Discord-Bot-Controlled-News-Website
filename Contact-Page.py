from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app) 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUBMISSIONS_FILE = os.path.join(BASE_DIR, 'data', 'contact-form-submissions.json')

def init_file():
    """Ensures the directory and a valid JSON array exist."""
    os.makedirs(os.path.dirname(SUBMISSIONS_FILE), exist_ok=True)
    if not os.path.exists(SUBMISSIONS_FILE) or os.stat(SUBMISSIONS_FILE).st_size == 0:
        with open(SUBMISSIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

@app.route('/submit-contact', methods=['POST'])
def submit_contact():
    init_file()
    try:
        new_submission = request.get_json()
        if not new_submission:
            return jsonify({"status": "error", "message": "No data received"}), 400

        with open(SUBMISSIONS_FILE, 'r', encoding='utf-8') as f:
            submissions = json.load(f)

        submissions.append(new_submission)
        with open(SUBMISSIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(submissions, f, indent=4)

        return jsonify({"status": "success"}), 200
    
    except json.JSONDecodeError:
        with open(SUBMISSIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump([new_submission], f, indent=4)
        return jsonify({"status": "success", "note": "file reset"}), 200
    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    init_file()
    print(f"Backend running at http://127.0.0.1:5000")
    app.run(port=5000, debug=True)