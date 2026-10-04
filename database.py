import sqlite3
import os
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voting_system.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        email_verified INTEGER DEFAULT 0,
        otp_code TEXT,
        otp_created_at TIMESTAMP,
        profile_photo TEXT,
        face_feature TEXT,
        has_voted INTEGER DEFAULT 0,
        voted_party_id INTEGER,
        voted_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (voted_party_id) REFERENCES parties(id)
    )
    """)
    
    # 2. Political Parties table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS parties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        candidate_name TEXT NOT NULL,
        symbol_type TEXT DEFAULT 'icon',
        symbol_image TEXT,
        symbol_icon TEXT DEFAULT 'fa-solid fa-landmark',
        color TEXT DEFAULT '#2563eb',
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 3. Votes table (digital ballot receipts)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        receipt_token TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        party_id INTEGER NOT NULL,
        match_score REAL,
        challenge_type TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (party_id) REFERENCES parties(id)
    )
    """)
    
    # 4. Admins table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        email TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Pre-seed default Admin if not exists
    cursor.execute("SELECT id FROM admins WHERE username = 'admin'")
    if not cursor.fetchone():
        admin_pass = generate_password_hash("admin123")
        cursor.execute(
            "INSERT INTO admins (username, password_hash, email) VALUES (?, ?, ?)",
            ("admin", admin_pass, "admin@election.gov")
        )
        
    # Pre-seed sample parties if none exist
    cursor.execute("SELECT COUNT(*) as count FROM parties")
    if cursor.fetchone()["count"] == 0:
        sample_parties = [
            (
                "Progressive Alliance",
                "Dr. Sarah Jenkins",
                "icon",
                None,
                "fa-solid fa-dove",
                "#2563eb",
                "Committed to healthcare, equal education, and renewable energy investments."
            ),
            (
                "Democratic Unity Front",
                "Robert Vance",
                "icon",
                None,
                "fa-solid fa-scale-balanced",
                "#059669",
                "Promoting transparent governance, fair justice, and economic stability."
            ),
            (
                "Future Innovation Party",
                "Marcus Chen",
                "icon",
                None,
                "fa-solid fa-bolt",
                "#7c3aed",
                "Pioneering digital infrastructure, technological advancement, and modern job creation."
            ),
            (
                "Eco-Green Coalition",
                "Elena Rostova",
                "icon",
                None,
                "fa-solid fa-tree",
                "#16a34a",
                "Championing climate resilience, clean waters, and sustainable communities."
            )
        ]
        cursor.executemany(
            "INSERT INTO parties (name, candidate_name, symbol_type, symbol_image, symbol_icon, color, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
            sample_parties
        )
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
