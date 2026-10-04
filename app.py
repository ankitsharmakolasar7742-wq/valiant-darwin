import os
import re
import json
import base64
import uuid
import random
from datetime import datetime
from functools import wraps

import cv2
import numpy as np
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, send_from_directory
)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db, init_db
from face_engine import FaceEngine

# Base directory setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads", "profiles")
PARTY_UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads", "parties")

os.makedirs(PROFILE_UPLOAD_DIR, exist_ok=True)
os.makedirs(PARTY_UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

app = Flask(__name__)
app.secret_key = "secure-biometric-voting-system-secret-key-2026"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload

# Initialize Face Engine
face_engine = FaceEngine()

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ----------------- Decorators -----------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin_id" not in session:
            flash("Administrator login required.", "warning")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated_function

# ----------------- User Routes -----------------
@app.route("/")
def index():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM parties")
    parties_count = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) as total FROM users")
    voters_count = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) as total FROM votes")
    votes_count = cursor.fetchone()["total"]
    conn.close()
    
    return render_template(
        "index.html",
        parties_count=parties_count,
        voters_count=voters_count,
        votes_count=votes_count
    )

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        # Validation checks
        if not (full_name and username and email and password):
            flash("All fields are required.", "danger")
            return render_template("register.html")
            
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")
            
        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("register.html")
            
        # Check photo upload
        if "profile_photo" not in request.files:
            flash("Please upload a profile photo for biometric registration.", "danger")
            return render_template("register.html")
            
        file = request.files["profile_photo"]
        if file.filename == "" or not allowed_file(file.filename):
            flash("Please upload a valid image file (JPG, PNG, WEBP).", "danger")
            return render_template("register.html")
            
        # Verify uniqueness of username and email
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            flash("Username is already taken. Please choose another.", "danger")
            return render_template("register.html")
            
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            flash("An account with this email address already exists.", "danger")
            return render_template("register.html")
            
        # Read and analyze uploaded image for face detection
        file_bytes = file.read()
        np_arr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if img is None:
            conn.close()
            flash("Failed to read image. Please try uploading a different photo.", "danger")
            return render_template("register.html")
            
        # Detect face & extract embedding
        face_data, bbox = face_engine.detect_face(img)
        if face_data is None:
            conn.close()
            flash("No clear face detected in the photo. Please upload a well-lit, front-facing portrait photo.", "danger")
            return render_template("register.html")
            
        feature = face_engine.extract_feature(img, face_data)
        if feature is None:
            conn.close()
            flash("Could not extract facial biometric features. Please try another photo.", "danger")
            return render_template("register.html")
            
        # Save photo to disk
        ext = file.filename.rsplit(".", 1)[1].lower()
        filename = f"{uuid.uuid4().hex[:12]}_{secure_filename(username)}.{ext}"
        filepath = os.path.join(PROFILE_UPLOAD_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(file_bytes)
            
        # Convert feature embedding to JSON string for database storage
        feature_json = json.dumps(feature.flatten().tolist())
        
        # Generate 6-digit OTP code for email verification
        otp_code = f"{random.randint(100000, 999999)}"
        password_hash = generate_password_hash(password)
        
        cursor.execute("""
            INSERT INTO users (
                full_name, username, email, password_hash,
                email_verified, otp_code, otp_created_at,
                profile_photo, face_feature
            ) VALUES (?, ?, ?, ?, 0, ?, CURRENT_TIMESTAMP, ?, ?)
        """, (full_name, username, email, password_hash, otp_code, filename, feature_json))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Store pending verification in session
        session["pending_user_id"] = user_id
        session["pending_email"] = email
        session["demo_otp"] = otp_code  # For interactive on-screen demo verification
        
        flash("Registration initiated! Please enter the 6-digit verification code sent to your email.", "info")
        return redirect(url_for("verify_email"))
        
    return render_template("register.html")

@app.route("/verify-email", methods=["GET", "POST"])
def verify_email():
    user_id = session.get("pending_user_id")
    email = session.get("pending_email")
    demo_otp = session.get("demo_otp")
    
    if not user_id:
        flash("No pending verification found. Please register or log in.", "warning")
        return redirect(url_for("register"))
        
    if request.method == "POST":
        submitted_otp = request.form.get("otp", "").strip()
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, otp_code, full_name FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            flash("User not found.", "danger")
            return redirect(url_for("register"))
            
        if user["otp_code"] == submitted_otp:
            # Mark email as verified
            cursor.execute("UPDATE users SET email_verified = 1, otp_code = NULL WHERE id = ?", (user_id,))
            conn.commit()
            conn.close()
            
            # Clear pending session keys
            session.pop("pending_user_id", None)
            session.pop("pending_email", None)
            session.pop("demo_otp", None)
            
            flash("Email verified successfully! You can now log in with your credentials.", "success")
            return redirect(url_for("login"))
        else:
            conn.close()
            flash("Invalid OTP code. Please check the code and try again.", "danger")
            return render_template("verify_email.html", email=email, demo_otp=demo_otp)
            
    return render_template("verify_email.html", email=email, demo_otp=demo_otp)

@app.route("/resend-otp", methods=["POST"])
def resend_otp():
    user_id = session.get("pending_user_id")
    if not user_id:
        flash("Session expired. Please register again.", "warning")
        return redirect(url_for("register"))
        
    new_otp = f"{random.randint(100000, 999999)}"
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET otp_code = ?, otp_created_at = CURRENT_TIMESTAMP WHERE id = ?", (new_otp, user_id))
    conn.commit()
    conn.close()
    
    session["demo_otp"] = new_otp
    flash(f"A new 6-digit OTP code has been sent to your email!", "info")
    return redirect(url_for("verify_email"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        if not (username and password):
            flash("Please enter both username and password.", "danger")
            return render_template("login.html")
            
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid username or password.", "danger")
            return render_template("login.html")
            
        if user["email_verified"] != 1:
            session["pending_user_id"] = user["id"]
            session["pending_email"] = user["email"]
            session["demo_otp"] = user["otp_code"]
            flash("Your email is not verified yet. Please verify your email to proceed.", "warning")
            return redirect(url_for("verify_email"))
            
        # Set session
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["full_name"] = user["full_name"]
        session["profile_photo"] = user["profile_photo"]
        
        flash(f"Welcome back, {user['full_name']}!", "success")
        return redirect(url_for("vote"))
        
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    session.pop("full_name", None)
    session.pop("profile_photo", None)
    flash("You have been successfully logged out.", "info")
    return redirect(url_for("login"))

# ----------------- Voting Screen & Biometrics -----------------
@app.route("/vote")
@login_required
def vote():
    user_id = session["user_id"]
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if user has already voted
    cursor.execute("""
        SELECT u.has_voted, u.voted_at, p.name as party_name, p.candidate_name, v.receipt_token
        FROM users u
        LEFT JOIN parties p ON u.voted_party_id = p.id
        LEFT JOIN votes v ON v.user_id = u.id
        WHERE u.id = ?
    """, (user_id,))
    voter_status = cursor.fetchone()
    
    # Fetch all registered political parties
    cursor.execute("SELECT * FROM parties ORDER BY id ASC")
    parties = cursor.fetchall()
    conn.close()
    
    has_voted = bool(voter_status["has_voted"]) if voter_status else False
    
    return render_template(
        "vote.html",
        user=session,
        has_voted=has_voted,
        voter_status=voter_status,
        parties=parties
    )

@app.route("/api/start-verification", methods=["POST"])
@login_required
def api_start_verification():
    """
    Initializes a new biometric verification session for the selected party.
    Randomly selects an anti-spoofing challenge (Blink, Turn Head Left, Turn Head Right, Smile).
    """
    data = request.get_json() or {}
    party_id = data.get("party_id")
    
    if not party_id:
        return jsonify({"success": False, "error": "Party ID is required."}), 400
        
    challenges = [
        {"type": "BLINK", "title": "Blink Eyes", "instruction": "Look directly at the camera and blink your eyes 2 times.", "icon": "fa-solid fa-eye"},
        {"type": "HEAD_LEFT", "title": "Turn Head Left", "instruction": "Slowly turn your head to the LEFT side.", "icon": "fa-solid fa-arrow-left"},
        {"type": "HEAD_RIGHT", "title": "Turn Head Right", "instruction": "Slowly turn your head to the RIGHT side.", "icon": "fa-solid fa-arrow-right"},
        {"type": "SMILE", "title": "Smile", "instruction": "Give a natural smile looking at the camera.", "icon": "fa-solid fa-face-smile"}
    ]
    
    selected_challenge = random.choice(challenges)
    
    # Store challenge & fresh session state in session
    session["current_party_id"] = party_id
    session["current_challenge"] = selected_challenge["type"]
    session["verification_state"] = {
        "blinks": 0,
        "eye_closed": False,
        "action_frames": 0,
        "challenge_passed": False,
        "face_match_passed": False
    }
    
    return jsonify({
        "success": True,
        "challenge": selected_challenge
    })

@app.route("/api/verify-frame", methods=["POST"])
@login_required
def api_verify_frame():
    """
    Processes a live video webcam frame sent from browser:
    - Analyzes liveness with MediaPipe (EAR, Head Pose Yaw, Smile)
    - Matches face with registered voter photo embedding using SFace
    - Returns real-time state, match score, and challenge progress
    """
    user_id = session.get("user_id")
    challenge_type = session.get("current_challenge", "BLINK")
    verification_state = session.get("verification_state", {})
    
    data = request.get_json() or {}
    image_b64 = data.get("image")
    
    if not image_b64:
        return jsonify({"success": False, "error": "No image data provided"}), 400
        
    try:
        # Strip header if present: data:image/jpeg;base64,...
        if "," in image_b64:
            image_b64 = image_b64.split(",", 1)[1]
            
        img_bytes = base64.b64decode(image_b64)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({"success": False, "error": "Failed to decode frame"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Decoding error: {str(e)}"}), 400
        
    # Retrieve user's registered face embedding from DB
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT face_feature FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row or not row["face_feature"]:
        return jsonify({"success": False, "error": "Voter face feature not found in database."}), 400
        
    registered_feature = np.array(json.loads(row["face_feature"]), dtype=np.float32).reshape(1, 128)
    
    # Evaluate frame
    eval_result = face_engine.evaluate_liveness_and_match(
        frame,
        registered_feature,
        challenge_type,
        verification_state
    )
    
    # Update session state with updated counters
    session["verification_state"] = eval_result["session_state"]
    if eval_result["challenge_passed"] and eval_result["is_matched"]:
        session["verification_state"]["verified"] = True
        session["verification_state"]["final_score"] = eval_result["match_pct"]
    
    return jsonify({
        "success": True,
        "face_detected": eval_result["face_detected"],
        "is_matched": eval_result["is_matched"],
        "match_pct": eval_result["match_pct"],
        "challenge_passed": eval_result["challenge_passed"],
        "progress": eval_result["progress"],
        "message": eval_result["message"],
        "can_submit": bool(eval_result["challenge_passed"] and eval_result["is_matched"])
    })

@app.route("/api/cast-vote", methods=["POST"])
@login_required
def api_cast_vote():
    """
    Cast official vote after face verification & liveness challenge are both met.
    Enforces atomic one-person-one-vote rule.
    """
    user_id = session.get("user_id")
    data = request.get_json() or {}
    party_id = data.get("party_id") or session.get("current_party_id")
    
    if not party_id:
        return jsonify({"success": False, "error": "Party selection missing."}), 400
        
    verification_state = session.get("verification_state", {})
    # Verify that liveness and face match were achieved
    if not (verification_state.get("challenge_passed") and verification_state.get("verified")):
        return jsonify({"success": False, "error": "Biometric verification not completed or failed."}), 403
        
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if user has already voted (prevents double-voting)
    cursor.execute("SELECT has_voted FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return jsonify({"success": False, "error": "User record not found."}), 404
        
    if user["has_voted"] == 1:
        conn.close()
        return jsonify({"success": False, "error": "You have already cast your vote in this election."}), 400
        
    # Generate unique cryptographic receipt token
    receipt_token = f"VOTE-{uuid.uuid4().hex[:8].upper()}-{uuid.uuid4().hex[:8].upper()}"
    match_score = verification_state.get("final_score", 95.0)
    challenge_type = session.get("current_challenge", "LIVENESS")
    
    # Atomic transaction
    try:
        cursor.execute("""
            INSERT INTO votes (receipt_token, user_id, party_id, match_score, challenge_type, timestamp)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (receipt_token, user_id, party_id, match_score, challenge_type))
        
        cursor.execute("""
            UPDATE users
            SET has_voted = 1, voted_party_id = ?, voted_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (party_id, user_id))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({"success": False, "error": f"Database error: {str(e)}"}), 500
        
    conn.close()
    
    # Clean up verification session state
    session.pop("verification_state", None)
    session.pop("current_party_id", None)
    session.pop("current_challenge", None)
    
    return jsonify({
        "success": True,
        "receipt_token": receipt_token,
        "redirect_url": url_for("vote_success", receipt_token=receipt_token)
    })

@app.route("/vote-success/<receipt_token>")
@login_required
def vote_success(receipt_token):
    user_id = session["user_id"]
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT v.*, p.name as party_name, p.candidate_name, p.symbol_icon, p.symbol_image, p.color, u.full_name, u.username
        FROM votes v
        JOIN parties p ON v.party_id = p.id
        JOIN users u ON v.user_id = u.id
        WHERE v.receipt_token = ? AND v.user_id = ?
    """, (receipt_token, user_id))
    vote_record = cursor.fetchone()
    conn.close()
    
    if not vote_record:
        flash("Vote receipt not found.", "warning")
        return redirect(url_for("vote"))
        
    return render_template("vote_success.html", receipt=vote_record)

# ----------------- Admin Portal -----------------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE username = ?", (username,))
        admin = cursor.fetchone()
        conn.close()
        
        if admin and check_password_hash(admin["password_hash"], password):
            session["admin_id"] = admin["id"]
            session["admin_username"] = admin["username"]
            flash("Welcome to the Election Administration Portal.", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid administrator credentials.", "danger")
            return render_template("admin_login.html")
            
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_id", None)
    session.pop("admin_username", None)
    flash("Admin logged out successfully.", "info")
    return redirect(url_for("admin_login"))

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Total statistics
    cursor.execute("SELECT COUNT(*) as count FROM users")
    total_voters = cursor.fetchone()["count"]
    
    cursor.execute("SELECT COUNT(*) as count FROM users WHERE email_verified = 1")
    verified_voters = cursor.fetchone()["count"]
    
    cursor.execute("SELECT COUNT(*) as count FROM votes")
    total_votes = cursor.fetchone()["count"]
    
    turnout_pct = round((total_votes / max(1, verified_voters)) * 100, 1)
    
    # 2. Parties and current vote counts
    cursor.execute("""
        SELECT p.*, COUNT(v.id) as vote_count
        FROM parties p
        LEFT JOIN votes v ON p.id = v.party_id
        GROUP BY p.id
        ORDER BY vote_count DESC, p.name ASC
    """)
    parties_with_votes = cursor.fetchall()
    
    # 3. Recent Voters list
    cursor.execute("""
        SELECT u.id, u.full_name, u.username, u.email, u.email_verified, u.has_voted, u.voted_at,
               u.profile_photo, p.name as voted_party_name
        FROM users u
        LEFT JOIN parties p ON u.voted_party_id = p.id
        ORDER BY u.created_at DESC
        LIMIT 50
    """)
    voters_list = cursor.fetchall()
    
    # 4. Recent Votes Audit Log
    cursor.execute("""
        SELECT v.*, u.full_name, u.username, p.name as party_name
        FROM votes v
        JOIN users u ON v.user_id = u.id
        JOIN parties p ON v.party_id = p.id
        ORDER BY v.timestamp DESC
        LIMIT 20
    """)
    recent_votes = cursor.fetchall()
    
    conn.close()
    
    return render_template(
        "admin_dashboard.html",
        total_voters=total_voters,
        verified_voters=verified_voters,
        total_votes=total_votes,
        turnout_pct=turnout_pct,
        parties=parties_with_votes,
        voters=voters_list,
        recent_votes=recent_votes
    )

@app.route("/admin/party/add", methods=["POST"])
@admin_required
def admin_add_party():
    name = request.form.get("name", "").strip()
    candidate_name = request.form.get("candidate_name", "").strip()
    color = request.form.get("color", "#2563eb").strip()
    description = request.form.get("description", "").strip()
    symbol_icon = request.form.get("symbol_icon", "fa-solid fa-landmark").strip()
    
    if not (name and candidate_name):
        flash("Party Name and Candidate Name are required.", "danger")
        return redirect(url_for("admin_dashboard"))
        
    symbol_image = None
    symbol_type = "icon"
    
    # Optional image file upload
    if "symbol_image" in request.files:
        file = request.files["symbol_image"]
        if file and file.filename != "" and allowed_file(file.filename):
            ext = file.filename.rsplit(".", 1)[1].lower()
            filename = f"party_{uuid.uuid4().hex[:8]}.{ext}"
            file.save(os.path.join(PARTY_UPLOAD_DIR, filename))
            symbol_image = filename
            symbol_type = "image"
            
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO parties (name, candidate_name, symbol_type, symbol_image, symbol_icon, color, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, candidate_name, symbol_type, symbol_image, symbol_icon, color, description))
        conn.commit()
        flash(f"Political party '{name}' registered successfully!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error adding party: {str(e)}", "danger")
    finally:
        conn.close()
        
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/party/delete/<int:party_id>", methods=["POST"])
@admin_required
def admin_delete_party(party_id):
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if party has received votes
    cursor.execute("SELECT COUNT(*) as count FROM votes WHERE party_id = ?", (party_id,))
    votes_count = cursor.fetchone()["count"]
    
    if votes_count > 0:
        conn.close()
        flash("Cannot delete a party that has already received votes.", "danger")
        return redirect(url_for("admin_dashboard"))
        
    cursor.execute("DELETE FROM parties WHERE id = ?", (party_id,))
    conn.commit()
    conn.close()
    
    flash("Party removed successfully.", "info")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/reset-election", methods=["POST"])
@admin_required
def admin_reset_election():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM votes")
    cursor.execute("UPDATE users SET has_voted = 0, voted_party_id = NULL, voted_at = NULL")
    conn.commit()
    conn.close()
    
    flash("All election votes have been reset for testing.", "info")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/api/live-stats")
@admin_required
def admin_api_live_stats():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.name, p.color, COUNT(v.id) as vote_count
        FROM parties p
        LEFT JOIN votes v ON p.id = v.party_id
        GROUP BY p.id
        ORDER BY p.id ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    labels = [r["name"] for r in rows]
    counts = [r["vote_count"] for r in rows]
    colors = [r["color"] or "#2563eb" for r in rows]
    
    return jsonify({
        "labels": labels,
        "counts": counts,
        "colors": colors,
        "total": sum(counts)
    })

# ----------------- Main Entrypoint -----------------
if __name__ == "__main__":
    init_db()
    print("Starting Face Detection Voting System on http://127.0.0.1:5000 ...")
    app.run(host="0.0.0.0", port=5000, debug=True)
