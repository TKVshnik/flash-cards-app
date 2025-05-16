import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__, static_folder='assets')
CORS(app)

def get_db_path():
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database.db')

def get_db_connection():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = None
    try:
        conn = get_db_connection()
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                front TEXT NOT NULL,
                back TEXT NOT NULL,
                known INTEGER DEFAULT 0,
                repetitions INTEGER DEFAULT 0,
                last_reviewed TEXT,
                next_review TEXT
            )
        """)

        c.execute("SELECT COUNT(*) as count FROM flashcards")
        if c.fetchone()['count'] == 0:
            c.execute("INSERT INTO flashcards (front, back) VALUES (?, ?)", ("Hello", "Привет"))
            c.execute("INSERT INTO flashcards (front, back) VALUES (?, ?)", ("Goodbye", "До свидания"))
        
        conn.commit()
    except Exception as e:
        print(f"Error initializing database: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

init_db()

# API Endpoints
@app.route('/api/cards', methods=['GET'])
def get_cards():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM flashcards")
    cards = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(cards)

@app.route('/api/cards', methods=['POST'])
def add_card():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    
    data = request.get_json()
    if not all(key in data for key in ['front', 'back']):
        return jsonify({'error': 'Missing required fields'}), 400

    conn = get_db_connection()
    try:
        c = conn.cursor()
        c.execute("INSERT INTO flashcards (front, back) VALUES (?, ?)", (data['front'], data['back']))
        conn.commit()
        return jsonify({'status': 'success'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/cards/<int:id>/known', methods=['PUT'])
def mark_known(id):
    conn = get_db_connection()
    try:
        c = conn.cursor()
        c.execute("""
            UPDATE flashcards 
            SET known = 1, 
                repetitions = repetitions + 1,
                last_reviewed = datetime('now'),
                next_review = datetime('now', '+1 day')
            WHERE id = ?
        """, (id,))
        conn.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/cards/<int:id>', methods=['DELETE'])
def delete_card(id):
    conn = get_db_connection()
    try:
        c = conn.cursor()
        c.execute("DELETE FROM flashcards WHERE id = ?", (id,))
        conn.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/progress', methods=['GET'])
def get_progress():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as total FROM flashcards")
    total = c.fetchone()['total']
    c.execute("SELECT COUNT(*) as known FROM flashcards WHERE known = 1")
    known = c.fetchone()['known']
    conn.close()
    return jsonify({
        'total': total,
        'known': known,
        'percentage': (known / total * 100) if total > 0 else 0
    })

# Static Files Serving
@app.route('/')
def index():
    return send_from_directory('assets', 'index.html')

@app.route('/learn.html')
def learn():
    return send_from_directory('assets', 'learn.html')

@app.route('/test.html')
def test():
    return send_from_directory('assets', 'test.html')

@app.route('/css/<path:filename>')
def serve_css(filename):
    css_path = os.path.join(app.static_folder, 'css', filename)
    if not os.path.exists(css_path):
        return jsonify({'error': 'File not found'}), 404
    return send_from_directory('assets/css', filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    js_path = os.path.join(app.static_folder, 'js', filename)
    if not os.path.exists(js_path):
        return jsonify({'error': 'File not found'}), 404
    return send_from_directory('assets/js', filename)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('assets', 'favicon.ico')

# Fallback for other assets
@app.route('/<path:path>')
def serve_assets(path):
    try:
        return send_from_directory('assets', path)
    except:
        return send_from_directory('assets', 'index.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)