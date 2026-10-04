# BioVote - AI Face Detection & Liveness Voting System

An AI-powered Biometric Electronic Voting System built with **Flask**, **OpenCV (YuNet & SFace)**, and **MediaPipe FaceMesh**. It prevents voter impersonation and photo spoofing with real-time biometric face matching and interactive liveness challenges.

---

## Key Features

### 1. Voter Registration & Face Enrollment
- Collects **Full Legal Name**, **Username**, **Email**, and **Password**.
- **Biometric Photo Enrollment**:
  - Upload a portrait image (`JPG`, `PNG`, `WEBP`) or capture directly using the live webcam.
  - Automatically validates the photo with **YuNet Face Detector** to ensure a single, clear face is detected.
  - Computes and securely stores a **128-dimensional facial biometric template** using **SFace**.

### 2. Email Verification with OTP
- Generates a **6-digit One-Time Password (OTP)** on registration.
- Features a **Simulated Email Dispatcher** banner with an **Auto-Fill** button for instant testing, along with a "Resend Code" option.
- Voters can only access the voting ballot once their email is verified.

### 3. Voter Login & Single-Vote Enforcement
- Secure username and password authentication with `werkzeug.security` salted hashing.
- Enforces an atomic **one-person-one-vote** rule. If a voter has already cast their ballot, the system displays their recorded ballot status and tamper-proof receipt.

### 4. Interactive Biometric Verification & Liveness Challenges
- When a voter clicks on any political party on the ballot, an interactive modal opens:
  - **Side-by-Side Dual Display**: Registered profile photo alongside live webcam video.
  - **Random Anti-Spoofing Challenge**: Randomly assigns one of four interactive physical challenges:
    1. **Blink Eyes**: Requires blinking both eyes twice (evaluated via Eye Aspect Ratio - EAR).
    2. **Turn Head Left**: Requires turning head to the left (evaluated via 3D Head Pose Yaw & Landmark ratios).
    3. **Turn Head Right**: Requires turning head to the right.
    4. **Smile**: Requires a natural smile (evaluated via mouth-to-face aspect ratio).
  - **Live Face Matching**: Real-time cosine similarity calculation between the webcam stream and the stored 128-d reference embedding.
  - **Dynamic Progress Bar**: Real-time progress percentage (0% to 100%) and instant feedback messages.
  - **Submit Ballot**: The green submission button activates only when both face match and liveness challenge are satisfied.

### 5. Official Digital Ballot Receipt
- Displays an official tamper-proof electronic ballot receipt with:
  - Cryptographic Receipt ID (e.g. `VOTE-8FA3-92BD`)
  - Voter Name & Username
  - Party and Candidate Selected
  - Biometric Face Match Percentage (e.g. 96.4%)
  - Liveness Challenge Type Verified
  - Timestamp & Tamper-Proof Digital Stamp
  - One-click **Print / Save Receipt** button.

### 6. Administration Portal
- **Admin Authentication**: Dedicated login at `/admin/login`.
  - **Default Username**: `admin`
  - **Default Password**: `admin123`
- **Party Management**:
  - Add new political parties and candidate names.
  - Choose party theme color using a color picker.
  - Select party symbol icon (Dove, Scales, Tree, Torch, Shield, Flag, Sun, etc.) or upload custom logo image.
  - Provide platform manifesto and slogans.
  - Delete parties with zero votes.
- **Real-Time Visual Analytics**:
  - Dynamic **Chart.js** bar and doughnut charts displaying live vote distribution.
  - Key metric cards: Total Enrolled Voters, Verified Voters, Ballots Cast, Voter Turnout %.
- **Voter Roster & Audit Log**:
  - Live table of all enrolled voters with email verification status, stored biometric indicator, ballot status, and voting timestamps.
- **Testing Controls**:
  - One-click **Reset All Votes** button for repeated evaluation cycles.

---

## Project Structure

```
valiant-darwin/
├── app.py                     # Main Flask application & routes
├── database.py                # Database connection, schemas, and pre-seeders
├── face_engine.py             # SFace face recognition & MediaPipe liveness detection
├── test_app.py                # Automated end-to-end test suite
├── requirements.txt           # Python dependencies
├── models/
│   ├── yunet.onnx             # Deep learning face detection model
│   └── sface.onnx             # Deep learning face recognition model (128-d embeddings)
├── static/
│   ├── sample_voter.jpg       # Sample test portrait for instant testing
│   ├── uploads/
│   │   ├── profiles/          # Registered voter reference photos
│   │   └── parties/           # Political party symbol uploads
├── templates/
│   ├── base.html              # Base layout with navbar, alerts, footer
│   ├── index.html             # Landing page with election overview
│   ├── register.html          # Voter registration (with camera snapshot support)
│   ├── verify_email.html      # Email OTP verification page
│   ├── login.html             # Voter login page
│   ├── vote.html              # Candidate ballot & biometric verification modal
│   ├── vote_success.html      # Digital ballot receipt & confirmation
│   ├── admin_login.html       # Admin portal login
│   └── admin_dashboard.html   # Admin dashboard with live charts & party manager
└── README.md
```

---

## How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Server
```bash
python app.py
```

### 3. Open in Browser
- **Voter Portal**: [http://127.0.0.1:5000](http://127.0.0.1:5000)
- **Admin Portal**: [http://127.0.0.1:5000/admin/login](http://127.0.0.1:5000/admin/login)
  - Username: `admin`
  - Password: `admin123`

---

## Testing the Full Workflow

1. Navigate to **[http://127.0.0.1:5000/register](http://127.0.0.1:5000/register)**.
2. Fill in your details. Click **"Use Camera"** to snap your face photo directly or upload `static/sample_voter.jpg`.
3. Submit to enter the **Email Verification** screen. Click the **"Auto-Fill"** button to load the generated 6-digit OTP and click **Verify Email**.
4. Log in using your registered username and password.
5. In the **Official Ballot**, browse the registered political parties.
6. Click **"Vote for Candidate"** on any party.
7. Allow webcam permissions:
   - Position your face inside the target oval.
   - Follow the assigned challenge (e.g., blink twice, turn head left, turn head right, or smile).
   - Once verified (green indicator), click **"SUBMIT OFFICIAL VOTE"**.
8. View and print your official **Digital Ballot Receipt**.
9. Visit the **Admin Portal** at `/admin/dashboard` to view the live charts update in real time!
