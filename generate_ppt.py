import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Initialize Presentation
prs = Presentation()
# Set widescreen 16:9 (13.333 x 7.5 inches)
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Color Palette Definition
COLOR_BG_DARK = RGBColor(15, 23, 42)      # Slate 900
COLOR_BG_LIGHT = RGBColor(248, 250, 252)  # Slate 50
COLOR_CARD = RGBColor(255, 255, 255)      # Pure White
COLOR_CARD_BORDER = RGBColor(226, 232, 240) # Slate 200
COLOR_PRIMARY = RGBColor(37, 99, 235)     # Royal Blue (Tailwind Blue 600)
COLOR_PRIMARY_DARK = RGBColor(29, 78, 216)# Dark Blue
COLOR_ACCENT = RGBColor(16, 185, 129)     # Emerald Green
COLOR_PURPLE = RGBColor(124, 58, 237)     # Violet
COLOR_TEXT_DARK = RGBColor(15, 23, 42)    # Slate 900
COLOR_TEXT_MUTED = RGBColor(100, 116, 139)# Slate 500
COLOR_TEXT_LIGHT = RGBColor(241, 245, 249)# Slate 100
COLOR_CODE_BG = RGBColor(30, 41, 59)      # Slate 800

def set_slide_background(slide, color):
    """Sets a solid color background for a slide."""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_header(slide, title_text, category_text="BIOVOTE PROJECT PRESENTATION", dark_mode=False):
    """Standardized modern header for content slides."""
    # Category / Pill
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.35))
    tf_cat = cat_box.text_frame
    tf_cat.word_wrap = True
    tf_cat.margin_left = tf_cat.margin_top = tf_cat.margin_bottom = tf_cat.margin_right = 0
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = COLOR_PRIMARY if not dark_mode else RGBColor(96, 165, 250)

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.5), Inches(0.7))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    tf_title.margin_left = tf_title.margin_top = tf_title.margin_bottom = tf_title.margin_right = 0
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.size = Pt(24)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_TEXT_DARK if not dark_mode else COLOR_TEXT_LIGHT

def add_card(slide, left, top, width, height, bg_color=COLOR_CARD, border_color=COLOR_CARD_BORDER):
    """Adds a clean rounded rectangular container card."""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    return shape

# ==============================================================================
# SLIDE 1: Title Slide (Dark Hero)
# ==============================================================================
slide1 = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_background(slide1, COLOR_BG_DARK)

# Subtle decorative card in hero
add_card(slide1, Inches(0.8), Inches(0.8), Inches(11.73), Inches(5.9), bg_color=RGBColor(30, 41, 59), border_color=RGBColor(51, 65, 85))

# Badge
badge = add_card(slide1, Inches(1.3), Inches(1.3), Inches(3.6), Inches(0.45), bg_color=COLOR_PRIMARY, border_color=None)
badge_tf = badge.text_frame
badge_tf.vertical_anchor = MSO_ANCHOR.MIDDLE
bp = badge_tf.paragraphs[0]
bp.text = "NEXT-GEN BIOMETRIC VOTING"
bp.alignment = PP_ALIGN.CENTER
bp.font.size = Pt(10)
bp.font.bold = True
bp.font.color.rgb = COLOR_TEXT_LIGHT

# Title & Subtitle box
tbox = slide1.shapes.add_textbox(Inches(1.3), Inches(2.0), Inches(10.5), Inches(2.8))
tf = tbox.text_frame
tf.word_wrap = True

p1 = tf.paragraphs[0]
p1.text = "BioVote: AI Face Detection &\nAnti-Spoofing Voting System"
p1.font.size = Pt(36)
p1.font.bold = True
p1.font.color.rgb = COLOR_TEXT_LIGHT
p1.space_after = Pt(14)

p2 = tf.add_paragraph()
p2.text = "A Complete Multi-Tier Electronic Voting Platform with Real-Time Deep Facial Recognition (YuNet + SFace) and Active Interactive Liveness Verification (MediaPipe 3D Mesh)"
p2.font.size = Pt(15)
p2.font.color.rgb = RGBColor(148, 163, 184)
p2.space_after = Pt(20)

# Metadata footer in hero
fbox = slide1.shapes.add_textbox(Inches(1.3), Inches(5.3), Inches(10.5), Inches(0.8))
ftf = fbox.text_frame
fp = ftf.paragraphs[0]
fp.text = "Technology Stack: Python 3.10 | Flask 3.1 | OpenCV 4.10 (SFace & YuNet) | MediaPipe | SQLite3 | Chart.js"
fp.font.size = Pt(12)
fp.font.bold = True
fp.font.color.rgb = RGBColor(96, 165, 250)

# ==============================================================================
# SLIDE 2: Problem Statement & Proposed Solution
# ==============================================================================
slide2 = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_background(slide2, COLOR_BG_LIGHT)
add_header(slide2, "Executive Problem Statement & Proposed Solution", "BACKGROUND & MOTIVATION")

# Left Column: The Problem
add_card(slide2, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2))
p_box = slide2.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.0), Inches(4.7))
ptf = p_box.text_frame
ptf.word_wrap = True

pp1 = ptf.paragraphs[0]
pp1.text = "Challenges in Modern Voting Systems"
pp1.font.size = Pt(18)
pp1.font.bold = True
pp1.font.color.rgb = RGBColor(225, 29, 72) # Rose Red
pp1.space_after = Pt(12)

problems = [
    ("Voter Impersonation & Proxy Voting", "Unauthorized individuals voting on behalf of others or using stolen identity cards."),
    ("Photo & Screen Replay Spoofing", "Attackers holding up static photographs, printed masks, or video playback from smartphone screens to fool cameras."),
    ("Lack of Automated Real-Time Verification", "Manual voter roll checks are slow, error-prone, and susceptible to electoral manipulation."),
    ("Double Voting Vulnerabilities", "Voters exploiting jurisdictional gaps or timing lags to cast multiple ballots.")
]
for title, desc in problems:
    p_item = ptf.add_paragraph()
    p_item.text = f"• {title}: "
    p_item.font.bold = True
    p_item.font.size = Pt(12)
    p_item.font.color.rgb = COLOR_TEXT_DARK
    
    p_desc = ptf.add_paragraph()
    p_desc.text = f"  {desc}"
    p_desc.font.size = Pt(11)
    p_desc.font.color.rgb = COLOR_TEXT_MUTED
    p_desc.space_after = Pt(6)

# Right Column: The Solution (BioVote)
add_card(slide2, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2))
s_box = slide2.shapes.add_textbox(Inches(7.1), Inches(1.8), Inches(5.1), Inches(4.7))
stf = s_box.text_frame
stf.word_wrap = True

sp1 = stf.paragraphs[0]
sp1.text = "The BioVote Biometric Solution"
sp1.font.size = Pt(18)
sp1.font.bold = True
sp1.font.color.rgb = COLOR_PRIMARY
sp1.space_after = Pt(12)

solutions = [
    ("Deep Facial Biometric Matching", "SFace deep neural model extracts 128-d facial embedding vector; compares real-time webcam frame with enrolled profile."),
    ("Active Challenge-Response Liveness", "Dynamically issues physical challenges (Blink, Turn Left, Turn Right, Smile) to defeat 2D photos, masks, and video replays."),
    ("Two-Factor Email OTP Enrollment", "Ensures authenticated identity before voting authorization."),
    ("Atomic Cryptographic Ballot Ledger", "One-person-one-vote strictly enforced via DB transactions with tamper-proof digital receipts.")
]
for title, desc in solutions:
    s_item = stf.add_paragraph()
    s_item.text = f"✓ {title}: "
    s_item.font.bold = True
    s_item.font.size = Pt(12)
    s_item.font.color.rgb = COLOR_ACCENT
    
    s_desc = stf.add_paragraph()
    s_desc.text = f"  {desc}"
    s_desc.font.size = Pt(11)
    s_desc.font.color.rgb = COLOR_TEXT_MUTED
    s_desc.space_after = Pt(6)

# ==============================================================================
# SLIDE 3: System Architecture & Data Flow
# ==============================================================================
slide3 = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_background(slide3, COLOR_BG_LIGHT)
add_header(slide3, "End-to-End System Architecture", "TECHNICAL ARCHITECTURE")

# 4 Layer Horizontal Cards
layers = [
    ("1. Client / Presentation Layer", "Tailwind CSS UI, WebRTC Live Video Stream, Responsive Ballot Cards, Interactive Anti-Spoofing Radar Modal, Chart.js Live Analytics.", COLOR_PRIMARY),
    ("2. Application API Layer", "Flask 3.1 Application, REST Endpoints (/register, /verify-otp, /api/verify-frame, /api/cast-vote, /admin/dashboard), Session Manager.", COLOR_PURPLE),
    ("3. AI & Computer Vision Core", "OpenCV YuNet (Face Detection & Alignment), OpenCV SFace (128-d Feature Extraction), MediaPipe (3D Mesh, EAR Blinks, solvePnP Head Pose).", COLOR_ACCENT),
    ("4. Data & Election Ledger", "SQLite Database with ACID transactions, Bcrypt/Werkzeug salted hashes, Cryptographic SHA-256 digital ballot receipts, Zero-Vote locks.", RGBColor(234, 88, 12))
]

top_pos = 1.6
for title, desc, col in layers:
    card = add_card(slide3, Inches(0.8), Inches(top_pos), Inches(11.73), Inches(1.15))
    # Accent indicator bar on left of card
    bar = slide3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(top_pos), Inches(0.18), Inches(1.15))
    bar.fill.solid()
    bar.fill.fore_color.rgb = col
    bar.line.fill.background()

    tbox = slide3.shapes.add_textbox(Inches(1.2), Inches(top_pos + 0.1), Inches(11.0), Inches(0.95))
    tf = tbox.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = col
    
    p2 = tf.add_paragraph()
    p2.text = desc
    p2.font.size = Pt(11)
    p2.font.color.rgb = COLOR_TEXT_MUTED
    
    top_pos += 1.35

# ==============================================================================
# SLIDE 4: Core Project Modules Breakdown
# ==============================================================================
slide4 = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_background(slide4, COLOR_BG_LIGHT)
add_header(slide4, "Project Modules Overview & Focus Areas", "SYSTEM MODULES")

module_cards = [
    ("MODULE 1 (DEEP DIVE)", "Biometric Face Recognition", "YuNet face detector + SFace deep neural net. Extracts 128-D biometric vector, aligns facial landmarks, computes Cosine Similarity score in real-time.", COLOR_PRIMARY, True),
    ("MODULE 2 (DEEP DIVE)", "Anti-Spoofing & Liveness", "MediaPipe 3D Landmark Mesh (468 points). Evaluates EAR for eye blinks, solvePnP for 3D head yaw rotation (Left/Right), and mouth aspect for smiles.", COLOR_ACCENT, True),
    ("MODULE 3", "Voter Registration & OTP", "Registration portal with instant webcam snapshot capture or photo upload. 6-digit OTP verification with simulated dispatcher.", COLOR_PURPLE, False),
    ("MODULE 4", "Admin Portal & Analytics", "Election Commission portal to register candidates/parties, upload emblems, view live Chart.js vote tallies, and audit voter rolls.", RGBColor(234, 88, 12), False)
]

for idx, (tag, title, desc, col, is_focus) in enumerate(module_cards):
    row = idx // 2
    col_idx = idx % 2
    x = Inches(0.8 + col_idx * 6.0)
    y = Inches(1.6 + row * 2.65)
    
    card = add_card(slide4, x, y, Inches(5.7), Inches(2.4), bg_color=COLOR_CARD)
    
    tbox = slide4.shapes.add_textbox(x + Inches(0.3), y + Inches(0.2), Inches(5.1), Inches(2.0))
    tf = tbox.text_frame
    tf.word_wrap = True
    
    p_tag = tf.paragraphs[0]
    p_tag.text = tag
    p_tag.font.size = Pt(10)
    p_tag.font.bold = True
    p_tag.font.color.rgb = col
    p_tag.space_after = Pt(4)
    
    p_title = tf.add_paragraph()
    p_title.text = title
    p_title.font.size = Pt(16)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_TEXT_DARK
    p_title.space_after = Pt(8)
    
    p_desc = tf.add_paragraph()
    p_desc.text = desc
    p_desc.font.size = Pt(11)
    p_desc.font.color.rgb = COLOR_TEXT_MUTED

# ==============================================================================
# SLIDE 5: MODULE 1 DEEP-DIVE - Architecture & Pipeline
# ==============================================================================
slide5 = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_background(slide5, COLOR_BG_LIGHT)
add_header(slide5, "MODULE 1: Biometric Face Recognition Architecture", "MODULE 1 IMPLEMENTATION (PART 1)")

# Top Architecture Diagram Blocks (5 horizontal sequential steps)
steps = [
    ("1. WebRTC Frame", "Canvas encodes base64 JPEG from client webcam"),
    ("2. YuNet Detection", "Locates bounding box + 5 facial landmarks"),
    ("3. Face Alignment", "recognizer.alignCrop() normalizes pose/tilt"),
    ("4. SFace Embeddings", "Computes 128-D compact float feature vector"),
    ("5. Cosine Matching", "Compares with stored profile embedding")
]

for i, (stitle, sdesc) in enumerate(steps):
    sx = Inches(0.8 + i * 2.4)
    scard = add_card(slide5, sx, Inches(1.6), Inches(2.2), Inches(1.6), bg_color=COLOR_CARD)
    
    stb = slide5.shapes.add_textbox(sx + Inches(0.15), Inches(1.7), Inches(1.9), Inches(1.4))
    stf = stb.text_frame
    stf.word_wrap = True
    
    sp1 = stf.paragraphs[0]
    sp1.text = stitle
    sp1.font.size = Pt(11)
    sp1.font.bold = True
    sp1.font.color.rgb = COLOR_PRIMARY
    sp1.space_after = Pt(4)
    
    sp2 = stf.add_paragraph()
    sp2.text = sdesc
    sp2.font.size = Pt(9.5)
    sp2.font.color.rgb = COLOR_TEXT_MUTED

# Bottom 2 Detail Cards
add_card(slide5, Inches(0.8), Inches(3.45), Inches(5.7), Inches(3.45))
b1 = slide5.shapes.add_textbox(Inches(1.05), Inches(3.6), Inches(5.2), Inches(3.1))
b1_tf = b1.text_frame
b1_tf.word_wrap = True

bp1 = b1_tf.paragraphs[0]
bp1.text = "Mathematical Model & Similarity Metric"
bp1.font.size = Pt(15)
bp1.font.bold = True
bp1.font.color.rgb = COLOR_TEXT_DARK
bp1.space_after = Pt(8)

math_notes = [
    ("Cosine Similarity Formula", "S(u, v) = (u · v) / (||u||₂ · ||v||₂)"),
    ("OpenCV SFace Benchmark Threshold", "Cosine Threshold: 0.363 (Calibrated for FAR 1e-3). Score >= 0.363 confirms verified identity."),
    ("Normalized Confidence Mapping", "Transforms raw cosine score (-1.0 to 1.0) into human-readable 0% - 100% confidence rating displayed live to the voter."),
    ("Biometric Storage Security", "Profile photo is converted to 128 float values stored as JSON string in SQLite DB for microsecond lookup.")
]
for mtitle, mdesc in math_notes:
    mp = b1_tf.add_paragraph()
    mp.text = f"• {mtitle}: "
    mp.font.bold = True
    mp.font.size = Pt(11)
    mp.font.color.rgb = COLOR_PRIMARY
    
    mp2 = b1_tf.add_paragraph()
    mp2.text = f"  {mdesc}"
    mp2.font.size = Pt(10)
    mp2.font.color.rgb = COLOR_TEXT_MUTED
    mp2.space_after = Pt(4)

add_card(slide5, Inches(6.8), Inches(3.45), Inches(5.7), Inches(3.45))
b2 = slide5.shapes.add_textbox(Inches(7.05), Inches(3.6), Inches(5.2), Inches(3.1))
b2_tf = b2.text_frame
b2_tf.word_wrap = True

bp2 = b2_tf.paragraphs[0]
bp2.text = "Why YuNet + SFace?"
bp2.font.size = Pt(15)
bp2.font.bold = True
bp2.font.color.rgb = COLOR_TEXT_DARK
bp2.space_after = Pt(8)

reasons = [
    ("Lightweight & High Speed", "YuNet model is only 232 KB; SFace model is 38.6 MB. Runs in real time (>30 FPS) purely on CPU without expensive GPUs."),
    ("Pose & Illumination Invariance", "Automatic affine landmark alignment handles slight head tilts, varying lighting, and distance from camera."),
    ("Deep Feature Embeddings", "Extracts facial geometric topology and deep neural textures rather than raw pixel comparison."),
    ("Zero External C++ Build Hassle", "Operates directly inside OpenCV 4.10 ONNX runtime without heavy dlib or Cmake compile dependencies.")
]
for rtitle, rdesc in reasons:
    rp = b2_tf.add_paragraph()
    rp.text = f"✓ {rtitle}: "
    rp.font.bold = True
    rp.font.size = Pt(11)
    rp.font.color.rgb = COLOR_ACCENT
    
    rp2 = b2_tf.add_paragraph()
    rp2.text = f"  {rdesc}"
    rp2.font.size = Pt(10)
    rp2.font.color.rgb = COLOR_TEXT_MUTED
    rp2.space_after = Pt(4)

# ==============================================================================
# SLIDE 6: MODULE 1 IMPLEMENTATION - Source Code Architecture
# ==============================================================================
slide6 = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_background(slide6, COLOR_BG_LIGHT)
add_header(slide6, "MODULE 1: Implementation Code Structure", "MODULE 1 IMPLEMENTATION (PART 2)")

# Code Container (Dark box)
code_card = add_card(slide6, Inches(0.8), Inches(1.6), Inches(7.5), Inches(5.2), bg_color=COLOR_CODE_BG, border_color=None)
ctb = slide6.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(7.1), Inches(4.9))
ctf = ctb.text_frame
ctf.word_wrap = True

code_snippet = """# face_engine.py - Core Recognition Implementation
class FaceEngine:
    def __init__(self):
        # 1. Initialize YuNet Face Detector
        self.detector = cv2.FaceDetectorYN_create(
            model=YUNET_PATH, config="", input_size=(320, 320),
            score_threshold=0.6, nms_threshold=0.3
        )
        # 2. Initialize SFace 128-d Recognizer
        self.recognizer = cv2.FaceRecognizerSF_create(
            model=SFACE_PATH, config=""
        )

    def extract_feature(self, bgr_img, face_data=None):
        if face_data is None:
            face_data, _ = self.detect_face(bgr_img)
        # Crop & align face using 5 geometric landmarks
        aligned_face = self.recognizer.alignCrop(bgr_img, face_data)
        return self.recognizer.feature(aligned_face) # 128-d float

    def compare_faces(self, feature1, feature2, cosine_threshold=0.363):
        score = self.recognizer.match(
            feature1, feature2, cv2.FaceRecognizerSF_FR_COSINE
        )
        is_match = bool(score >= cosine_threshold)
        pct = min(100.0, 70.0 + ((score - 0.363) / 0.287) * 30.0)
        return is_match, float(score), round(pct, 1)"""

cp = ctf.paragraphs[0]
cp.text = code_snippet
cp.font.name = "Consolas"
cp.font.size = Pt(9.5)
cp.font.color.rgb = RGBColor(226, 232, 240)

# Right Side Card: Code Key Takeaways
add_card(slide6, Inches(8.5), Inches(1.6), Inches(4.0), Inches(5.2))
rtb = slide6.shapes.add_textbox(Inches(8.75), Inches(1.8), Inches(3.5), Inches(4.7))
rtf = rtb.text_frame
rtf.word_wrap = True

rp1 = rtf.paragraphs[0]
rp1.text = "Key Code Highlights"
rp1.font.size = Pt(16)
rp1.font.bold = True
rp1.font.color.rgb = COLOR_PRIMARY
rp1.space_after = Pt(12)

highlights = [
    ("Registration Validation", "Ensures uploaded portrait contains exactly 1 detectable face before account creation."),
    ("Pre-computed Embeddings", "The 128-d array is serialized to database during signup. Only the live webcam frame requires inference during voting."),
    ("Sub-15ms Matching", "Cosine similarity between two 128-d vectors executes in < 0.2 milliseconds, enabling 2-3 live evaluations per second without server lag.")
]
for htitle, hdesc in highlights:
    hp = rtf.add_paragraph()
    hp.text = f"• {htitle}:"
    hp.font.bold = True
    hp.font.size = Pt(11)
    hp.font.color.rgb = COLOR_TEXT_DARK
    
    hp2 = rtf.add_paragraph()
    hp2.text = f"{hdesc}"
    hp2.font.size = Pt(10)
    hp2.font.color.rgb = COLOR_TEXT_MUTED
    hp2.space_after = Pt(8)

# ==============================================================================
# SLIDE 7: MODULE 2 DEEP-DIVE - Interactive Anti-Spoofing & Liveness
# ==============================================================================
slide7 = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_background(slide7, COLOR_BG_LIGHT)
add_header(slide7, "MODULE 2: Real-Time Anti-Spoofing & Liveness Engine", "MODULE 2 IMPLEMENTATION (PART 1)")

# Top Notice Banner
tb = add_card(slide7, Inches(0.8), Inches(1.5), Inches(11.73), Inches(0.8), bg_color=RGBColor(239, 246, 255), border_color=RGBColor(191, 219, 254))
tbtf = tb.text_frame
tbtf.vertical_anchor = MSO_ANCHOR.MIDDLE
tbp = tbtf.paragraphs[0]
tbp.text = "Active Challenge-Response Biometrics: Solves the vulnerability of static photo attacks and smartphone video replays by assigning a randomly generated physical challenge that must be performed in real time."
tbp.font.size = Pt(11)
tbp.font.bold = True
tbp.font.color.rgb = COLOR_PRIMARY_DARK

# 4 Challenge Cards Grid (2x2)
challenges = [
    ("1. Eye Blink Challenge (EAR)", "Monitors Left Eye (landmarks 33, 160, 158, 133, 153, 144) & Right Eye (362, 385, 387, 263, 373, 380). Detects rapid EAR dip < 0.20 and rebound. Requires 2 sequential blinks.", COLOR_PRIMARY),
    ("2. Head Turn Left Challenge", "MediaPipe 3D landmark mesh calculates head yaw angle via solvePnP & landmark ratios. User must turn head to their left and hold for 4 consecutive frames.", COLOR_ACCENT),
    ("3. Head Turn Right Challenge", "Evaluates mirrored 3D yaw angle threshold (Yaw < -14° or ratio > 0.62). Confirms volumetric 3D head movement impossible with a flat 2D photograph.", COLOR_PURPLE),
    ("4. Dynamic Smile Challenge", "Measures mouth width (landmarks 61 & 291) relative to face width (landmarks 234 & 454). Verifies genuine smile when ratio exceeds 0.44.", RGBColor(234, 88, 12))
]

for idx, (title, desc, col) in enumerate(challenges):
    r = idx // 2
    c = idx % 2
    cx = Inches(0.8 + c * 6.0)
    cy = Inches(2.55 + r * 2.3)
    
    card = add_card(slide7, cx, cy, Inches(5.7), Inches(2.1))
    
    # Accent indicator
    cbar = slide7.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, cy, Inches(0.15), Inches(2.1))
    cbar.fill.solid()
    cbar.fill.fore_color.rgb = col
    cbar.line.fill.background()
    
    ctb = slide7.shapes.add_textbox(cx + Inches(0.35), cy + Inches(0.15), Inches(5.1), Inches(1.8))
    ctf = ctb.text_frame
    ctf.word_wrap = True
    
    cp1 = ctf.paragraphs[0]
    cp1.text = title
    cp1.font.size = Pt(14)
    cp1.font.bold = True
    cp1.font.color.rgb = col
    cp1.space_after = Pt(6)
    
    cp2 = ctf.add_paragraph()
    cp2.text = desc
    cp2.font.size = Pt(10.5)
    cp2.font.color.rgb = COLOR_TEXT_MUTED

# ==============================================================================
# SLIDE 8: MODULE 2 IMPLEMENTATION - Formulas & Vision Logic
# ==============================================================================
slide8 = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_background(slide8, COLOR_BG_LIGHT)
add_header(slide8, "MODULE 2: Liveness Mathematical Formulations & Code", "MODULE 2 IMPLEMENTATION (PART 2)")

# Left Card: Eye Aspect Ratio & 3D Pose Mathematics
add_card(slide8, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.2))
m_box = slide8.shapes.add_textbox(Inches(1.05), Inches(1.8), Inches(5.2), Inches(4.8))
mtf = m_box.text_frame
mtf.word_wrap = True

mp1 = mtf.paragraphs[0]
mp1.text = "Mathematical Formulations"
mp1.font.size = Pt(16)
mp1.font.bold = True
mp1.font.color.rgb = COLOR_PRIMARY
mp1.space_after = Pt(10)

formulations = [
    ("Eye Aspect Ratio (EAR) Formulation", "EAR = (||p₂ - p₆|| + ||p₃ - p₅||) / (2 · ||p₁ - p₄||)\n• p₁, p₄: horizontal corners; p₂, p₆ and p₃, p₅: vertical eyelids.\n• Open eyes: EAR ~ 0.28 - 0.35. Closed eyes: EAR < 0.20."),
    ("3D Head Pose Estimation (solvePnP)", "Maps 3D generic facial points to 2D image coordinates:\n• Nose (1), Chin (152), Left Eye (33), Right Eye (263), Mouth (61, 291).\n• Solves camera matrix & Rodrigues rotation vector R.\n• Computes Euler Yaw: Yaw = arctan2(-R[2,0], sqrt(R[0,0]² + R[1,0]²))"),
    ("Smile Ratio Formulation", "Smile Ratio = ||Mouth_Left - Mouth_Right|| / ||Cheek_L - Cheek_R||\n• Genuine smile triggers when ratio > 0.44 for >= 4 frames.")
]
for ftitle, fdesc in formulations:
    fp = mtf.add_paragraph()
    fp.text = f"• {ftitle}:"
    fp.font.bold = True
    fp.font.size = Pt(11)
    fp.font.color.rgb = COLOR_TEXT_DARK
    
    fp2 = mtf.add_paragraph()
    fp2.text = f"{fdesc}"
    fp2.font.size = Pt(9.5)
    fp2.font.color.rgb = COLOR_TEXT_MUTED
    fp2.space_after = Pt(6)

# Right Card: Code Implementation snippet
add_card(slide8, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2), bg_color=COLOR_CODE_BG, border_color=None)
c_box = slide8.shapes.add_textbox(Inches(7.0), Inches(1.75), Inches(5.3), Inches(4.9))
ctf2 = c_box.text_frame
ctf2.word_wrap = True

code_liveness = """# Liveness Challenge Verification Snippet
def evaluate_liveness_and_match(self, frame, reg_feat,
                                challenge_type, state):
    results = self.face_mesh.process(rgb_frame)
    lms = results.multi_face_landmarks[0].landmark
    
    # 1. Evaluate Blink
    if challenge_type == "BLINK":
        ear = (self._ear(lms, L_EYE) + self._ear(lms, R_EYE)) / 2
        if ear < 0.20:
            state["eye_closed"] = True
        elif state.get("eye_closed"):
            state["blinks"] += 1
            state["eye_closed"] = False
        if state["blinks"] >= 2:
            state["challenge_passed"] = True

    # 2. Evaluate 3D Head Yaw
    elif challenge_type == "HEAD_LEFT":
        pitch, yaw, roll = self._estimate_head_pose(lms)
        if yaw > 14.0 or ratio < 0.38:
            state["action_frames"] += 1
            if state["action_frames"] >= 4:
                state["challenge_passed"] = True"""

cp2 = ctf2.paragraphs[0]
cp2.text = code_liveness
cp2.font.name = "Consolas"
cp2.font.size = Pt(9.0)
cp2.font.color.rgb = RGBColor(226, 232, 240)

# ==============================================================================
# SLIDE 9: Complete Voter Journey & Cryptographic Receipts
# ==============================================================================
slide9 = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_background(slide9, COLOR_BG_LIGHT)
add_header(slide9, "Voter Journey & Tamper-Proof Ballot Receipts", "VOTER EXPERIENCE")

v_steps = [
    ("Step 1: Enrollment", "Voter registers credentials and captures/uploads profile portrait. YuNet verifies face presence; SFace stores 128-d biometric feature vector.", "fa-user-plus"),
    ("Step 2: Email OTP", "System issues a 6-digit OTP code to voter email. Enforces email ownership and identity verification before ballot access.", "fa-envelope-open-text"),
    ("Step 3: Party Ballot", "Voter logs in and selects political party/candidate. Launching vote triggers the camera scanner modal.", "fa-check-to-slot"),
    ("Step 4: Biometric Match", "Simultaneous dual-verification: Live face matched with profile photo (>70% confidence) AND assigned liveness challenge fulfilled.", "fa-expand"),
    ("Step 5: Digital Receipt", "System records vote atomically. Generates tamper-proof receipt (VOTE-XXXXXXXX-XXXXXXXX) with biometric match score & timestamp.", "fa-receipt")
]

for idx, (title, desc, icon) in enumerate(v_steps):
    vy = Inches(1.6 + idx * 1.05)
    card = add_card(slide9, Inches(0.8), vy, Inches(11.73), Inches(0.92))
    
    # Step Number Pill
    spill = add_card(slide9, Inches(1.0), vy + Inches(0.18), Inches(1.8), Inches(0.55), bg_color=COLOR_PRIMARY, border_color=None)
    sptf = spill.text_frame
    sptf.vertical_anchor = MSO_ANCHOR.MIDDLE
    spp = sptf.paragraphs[0]
    spp.text = f"PHASE {idx+1}"
    spp.alignment = PP_ALIGN.CENTER
    spp.font.size = Pt(11)
    spp.font.bold = True
    spp.font.color.rgb = COLOR_TEXT_LIGHT
    
    stb = slide9.shapes.add_textbox(Inches(3.0), vy + Inches(0.1), Inches(9.3), Inches(0.75))
    stf = stb.text_frame
    stf.word_wrap = True
    
    sp1 = stf.paragraphs[0]
    sp1.text = title
    sp1.font.size = Pt(13)
    sp1.font.bold = True
    sp1.font.color.rgb = COLOR_TEXT_DARK
    
    sp2 = stf.add_paragraph()
    sp2.text = desc
    sp2.font.size = Pt(10)
    sp2.font.color.rgb = COLOR_TEXT_MUTED

# ==============================================================================
# SLIDE 10: Admin Supervisory Portal & Live Analytics
# ==============================================================================
slide10 = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_background(slide10, COLOR_BG_LIGHT)
add_header(slide10, "Election Commission Supervisory Portal", "ADMINISTRATION & ANALYTICS")

admin_features = [
    ("Dynamic Candidate / Party Management", "Administrators can register new political parties, enter candidate names, pick theme branding colors, select party emblem icons, or upload custom high-resolution logos.", COLOR_PRIMARY),
    ("Real-Time Chart.js Visual Tallies", "Interactive bar charts and doughnut charts visualize vote share and live candidate rankings. Endpoint /admin/api/live-stats enables auto-refreshing analytics.", COLOR_ACCENT),
    ("Comprehensive Voter Roster & Audit", "Displays all enrolled citizens, email verification status, facial biometric indicators, voting timestamps, and party voted for.", COLOR_PURPLE),
    ("Election Integrity & Testing Controls", "Zero-vote locks protect parties with active votes. Dedicated 'Reset All Votes' tool enables multi-round testing without altering voter credentials.", RGBColor(234, 88, 12))
]

for idx, (title, desc, col) in enumerate(admin_features):
    r = idx // 2
    c = idx % 2
    cx = Inches(0.8 + c * 6.0)
    cy = Inches(1.6 + r * 2.65)
    
    card = add_card(slide10, cx, cy, Inches(5.7), Inches(2.4))
    
    cbar = slide10.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, cy, Inches(0.15), Inches(2.4))
    cbar.fill.solid()
    cbar.fill.fore_color.rgb = col
    cbar.line.fill.background()
    
    ctb = slide10.shapes.add_textbox(cx + Inches(0.35), cy + Inches(0.2), Inches(5.1), Inches(2.0))
    ctf = ctb.text_frame
    ctf.word_wrap = True
    
    cp1 = ctf.paragraphs[0]
    cp1.text = title
    cp1.font.size = Pt(15)
    cp1.font.bold = True
    cp1.font.color.rgb = col
    cp1.space_after = Pt(8)
    
    cp2 = ctf.add_paragraph()
    cp2.text = desc
    cp2.font.size = Pt(11)
    cp2.font.color.rgb = COLOR_TEXT_MUTED

# ==============================================================================
# SLIDE 11: Technology Stack & Performance Summary
# ==============================================================================
slide11 = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_background(slide11, COLOR_BG_LIGHT)
add_header(slide11, "Technology Stack & Performance Metrics", "SYSTEM SPECIFICATIONS")

# Table of Tech Stack
rows = 6
cols = 3
left = Inches(0.8)
top = Inches(1.6)
width = Inches(11.73)
height = Inches(4.8)

table_shape = slide11.shapes.add_table(rows, cols, left, top, width, height)
table = table_shape.table
table.columns[0].width = Inches(2.8)
table.columns[1].width = Inches(4.5)
table.columns[2].width = Inches(4.43)

headers = ["Component / Layer", "Technology Utilized", "Key Function & Performance Metric"]
data = [
    ("Web Framework & Routing", "Python 3.10 + Flask 3.1 + Werkzeug", "Microsecond REST routing, session management, secure password hashing"),
    ("Face Detection Model", "OpenCV YuNet (ONNX Model - 232 KB)", "Real-time CNN detection of bounding box + 5 facial landmarks in < 12ms"),
    ("Face Recognition Model", "OpenCV SFace (ONNX Model - 38.6 MB)", "Generates 128-d facial embeddings. Cosine similarity threshold 0.363"),
    ("Liveness / 3D Mesh", "Google MediaPipe FaceMesh (0.10.14)", "468 3D landmarks for real-time EAR (blinks) and solvePnP head yaw"),
    ("Database & Transactions", "SQLite3 with ACID Foreign Keys", "Enforces atomic one-voter-one-vote rule and generates unique audit tokens")
]

for c_idx, h in enumerate(headers):
    cell = table.cell(0, c_idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = COLOR_BG_DARK
    p = cell.text_frame.paragraphs[0]
    p.text = h
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEXT_LIGHT

for r_idx, row_data in enumerate(data):
    for c_idx, val in enumerate(row_data):
        cell = table.cell(r_idx + 1, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_CARD if r_idx % 2 == 0 else RGBColor(241, 245, 249)
        p = cell.text_frame.paragraphs[0]
        p.text = val
        p.font.size = Pt(10.5)
        p.font.color.rgb = COLOR_TEXT_DARK if c_idx == 0 else COLOR_TEXT_MUTED
        if c_idx == 0:
            p.font.bold = True

# ==============================================================================
# SLIDE 12: Conclusion & Future Scope (Dark Hero)
# ==============================================================================
slide12 = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_background(slide12, COLOR_BG_DARK)

add_card(slide12, Inches(0.8), Inches(0.8), Inches(11.73), Inches(5.9), bg_color=RGBColor(30, 41, 59), border_color=RGBColor(51, 65, 85))

tbox = slide12.shapes.add_textbox(Inches(1.3), Inches(1.2), Inches(10.5), Inches(5.0))
tf = tbox.text_frame
tf.word_wrap = True

p1 = tf.paragraphs[0]
p1.text = "Conclusion & Future Enhancements"
p1.font.size = Pt(28)
p1.font.bold = True
p1.font.color.rgb = COLOR_TEXT_LIGHT
p1.space_after = Pt(14)

conclusions = [
    ("Electoral Integrity Secured", "BioVote successfully eliminates impersonation and proxy voting through dual-layer face recognition and dynamic interactive liveness challenges."),
    ("High Performance & Zero Cloud Reliance", "Runs completely on edge/local systems using lightweight ONNX and MediaPipe models with zero GPU dependencies."),
    ("Future Scope: Blockchain Ledger", "Integration with decentralized Ethereum / Hyperledger blockchains for immutable public vote tally verification."),
    ("Future Scope: Multi-Spectral Liveness", "Incorporating near-infrared (NIR) or 3D depth-sensing cameras for anti-deepfake defense against hyper-realistic silicone masks.")
]
for ctitle, cdesc in conclusions:
    cp = tf.add_paragraph()
    cp.text = f"• {ctitle}: "
    cp.font.bold = True
    cp.font.size = Pt(13)
    cp.font.color.rgb = RGBColor(96, 165, 250)
    
    cp2 = tf.add_paragraph()
    cp2.text = f"  {cdesc}"
    cp2.font.size = Pt(11)
    cp2.font.color.rgb = RGBColor(203, 213, 225)
    cp2.space_after = Pt(8)

p_thanks = tf.add_paragraph()
p_thanks.text = "\nThank You! Open for Questions & Live Demonstration."
p_thanks.font.size = Pt(16)
p_thanks.font.bold = True
p_thanks.font.color.rgb = COLOR_ACCENT

# Save Presentation
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "BioVote_Presentation.pptx")
prs.save(output_path)
print(f"Presentation saved successfully to {output_path}")
