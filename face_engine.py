import os
import cv2
import numpy as np
import mediapipe as mp

# Path to ONNX models
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
YUNET_PATH = os.path.join(BASE_DIR, "models", "yunet.onnx")
SFACE_PATH = os.path.join(BASE_DIR, "models", "sface.onnx")

class FaceEngine:
    def __init__(self):
        # 1. Initialize YuNet Face Detector
        # Default input size (will be updated dynamically per image)
        self.detector = cv2.FaceDetectorYN_create(
            model=YUNET_PATH,
            config="",
            input_size=(320, 320),
            score_threshold=0.6,
            nms_threshold=0.3,
            top_k=5000
        )
        
        # 2. Initialize SFace Face Recognizer
        self.recognizer = cv2.FaceRecognizerSF_create(
            model=SFACE_PATH,
            config=""
        )
        
        # 3. Initialize MediaPipe Face Mesh for Liveness
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # 3D model points for Head Pose Estimation (PnP)
        self.model_points = np.array([
            (0.0, 0.0, 0.0),             # Nose tip (landmark 1)
            (0.0, -330.0, -65.0),        # Chin (landmark 152)
            (-225.0, 170.0, -135.0),     # Left eye corner (landmark 33)
            (225.0, 170.0, -135.0),      # Right eye corner (landmark 263)
            (-150.0, -150.0, -125.0),    # Left mouth corner (landmark 61)
            (150.0, -150.0, -125.0)      # Right mouth corner (landmark 291)
        ], dtype=np.float64)

    def detect_face(self, bgr_img):
        """Detect primary face in image using YuNet. Returns (face_data, bbox) or (None, None)."""
        h, w = bgr_img.shape[:2]
        self.detector.setInputSize((w, h))
        _, faces = self.detector.detect(bgr_img)
        
        if faces is None or len(faces) == 0:
            return None, None
            
        # Select the largest face by area
        best_face = None
        max_area = 0
        for f in faces:
            box = f[0:4].astype(int)
            area = box[2] * box[3]
            if area > max_area:
                max_area = area
                best_face = f
                
        bbox = best_face[0:4].astype(int)
        return best_face, bbox

    def extract_feature(self, bgr_img, face_data=None):
        """Extract 128-d face embedding from image using SFace."""
        if face_data is None:
            face_data, _ = self.detect_face(bgr_img)
            
        if face_data is None:
            return None
            
        aligned_face = self.recognizer.alignCrop(bgr_img, face_data)
        feature = self.recognizer.feature(aligned_face)
        return feature

    def compare_faces(self, feature1, feature2, cosine_threshold=0.363):
        """
        Compare two feature embeddings using Cosine Similarity.
        OpenCV SFace recommended cosine threshold is 0.363 for FAR 1e-3.
        Returns: (is_match: bool, similarity_score: float, match_percentage: float)
        """
        if feature1 is None or feature2 is None:
            return False, 0.0, 0.0
            
        score = self.recognizer.match(feature1, feature2, cv2.FaceRecognizerSF_FR_COSINE)
        
        # Calculate human-friendly percentage (0 to 100%)
        # Around 0.363 is considered matching (~70%). Higher (0.5 - 0.7+) is a very strong match (>85-95%)
        pct = 0.0
        if score > 0:
            # Linear mapping: 0.15 = 30%, 0.363 = 70%, 0.65+ = 98-100%
            if score < 0.363:
                pct = max(0.0, (score / 0.363) * 69.0)
            else:
                pct = min(100.0, 70.0 + ((score - 0.363) / (0.65 - 0.363)) * 30.0)
                
        is_match = score >= cosine_threshold
        return is_match, float(score), round(pct, 1)

    def _calculate_ear(self, landmarks, eye_indices, img_w, img_h):
        """Eye Aspect Ratio (EAR) for blink detection."""
        # eye_indices: [p1, p2, p3, p4, p5, p6]
        # p1: corner outer, p4: corner inner
        # p2, p6: top/bottom outer; p3, p5: top/bottom inner
        pts = []
        for idx in eye_indices:
            lm = landmarks[idx]
            pts.append(np.array([lm.x * img_w, lm.y * img_h]))
            
        # Vertical distances
        v1 = np.linalg.norm(pts[1] - pts[5])
        v2 = np.linalg.norm(pts[2] - pts[4])
        # Horizontal distance
        h = np.linalg.norm(pts[0] - pts[3])
        
        if h == 0:
            return 0.3
        return (v1 + v2) / (2.0 * h)

    def _estimate_head_pose(self, landmarks, img_w, img_h):
        """Estimate Head Yaw, Pitch, Roll in degrees using solvePnP."""
        # 2D points corresponding to model_points
        # 1: nose tip, 152: chin, 33: left eye outer, 263: right eye outer, 61: left mouth, 291: right mouth
        indices = [1, 152, 33, 263, 61, 291]
        image_points = []
        for idx in indices:
            lm = landmarks[idx]
            image_points.append([lm.x * img_w, lm.y * img_h])
        image_points = np.array(image_points, dtype=np.float64)
        
        # Camera matrix approximation
        focal_length = img_w
        center = (img_w / 2, img_h / 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype=np.float64)
        
        dist_coeffs = np.zeros((4, 1))
        success, rvec, tvec = cv2.solvePnP(
            self.model_points,
            image_points,
            camera_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        
        if not success:
            return 0.0, 0.0, 0.0
            
        rmat, _ = cv2.Rodrigues(rvec)
        # Compute Euler angles
        # angles: [pitch, yaw, roll]
        sy = np.sqrt(rmat[0, 0] ** 2 + rmat[1, 0] ** 2)
        singular = sy < 1e-6
        if not singular:
            pitch = np.arctan2(rmat[2, 1], rmat[2, 2])
            yaw = np.arctan2(-rmat[2, 0], sy)
            roll = np.arctan2(rmat[1, 0], rmat[0, 0])
        else:
            pitch = np.arctan2(-rmat[1, 2], rmat[1, 1])
            yaw = np.arctan2(-rmat[2, 0], sy)
            roll = 0
            
        return float(np.degrees(pitch)), float(np.degrees(yaw)), float(np.degrees(roll))

    def evaluate_liveness_and_match(self, bgr_img, registered_feature, challenge_type, session_state):
        """
        Processes a live video frame:
        1. Checks face detection and computes match against registered profile.
        2. Evaluates the interactive liveness challenge (Blink, Turn Left, Turn Right, Smile).
        3. Updates session_state and returns real-time feedback and progress.
        """
        h, w = bgr_img.shape[:2]
        rgb_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
        
        results = self.face_mesh.process(rgb_img)
        
        response = {
            "face_detected": False,
            "is_matched": False,
            "match_score": 0.0,
            "match_pct": 0.0,
            "challenge_type": challenge_type,
            "challenge_passed": False,
            "progress": 0,
            "message": "Looking for face in camera...",
            "session_state": session_state
        }
        
        if not results.multi_face_landmarks:
            response["message"] = "No face detected. Please face the camera directly."
            return response
            
        landmarks = results.multi_face_landmarks[0].landmark
        response["face_detected"] = True
        
        # 1. Face Match Verification
        live_feature = self.extract_feature(bgr_img)
        if live_feature is not None and registered_feature is not None:
            is_match, score, pct = self.compare_faces(registered_feature, live_feature)
            response["is_matched"] = is_match
            response["match_score"] = score
            response["match_pct"] = pct
        else:
            response["is_matched"] = False
            response["match_pct"] = 0.0
            
        # 2. Extract Biometric Landmarks & Angles
        # Left Eye indices: [33, 160, 158, 133, 153, 144]
        # Right Eye indices: [362, 385, 387, 263, 373, 380]
        left_ear = self._calculate_ear(landmarks, [33, 160, 158, 133, 153, 144], w, h)
        right_ear = self._calculate_ear(landmarks, [362, 385, 387, 263, 373, 380], w, h)
        avg_ear = (left_ear + right_ear) / 2.0
        
        pitch, yaw, roll = self._estimate_head_pose(landmarks, w, h)
        
        # Smile Ratio: distance between mouth corners (61, 291) divided by face width (234, 454)
        m_left = np.array([landmarks[61].x * w, landmarks[61].y * h])
        m_right = np.array([landmarks[291].x * w, landmarks[291].y * h])
        f_left = np.array([landmarks[234].x * w, landmarks[234].y * h])
        f_right = np.array([landmarks[454].x * w, landmarks[454].y * h])
        
        mouth_width = np.linalg.norm(m_left - m_right)
        face_width = np.linalg.norm(f_left - f_right)
        smile_ratio = mouth_width / max(1.0, face_width)
        
        # Initialize or retrieve session state variables
        # state keeps track of challenge milestones (e.g. blinks, movement frames)
        if "blinks" not in session_state:
            session_state["blinks"] = 0
            session_state["eye_closed"] = False
        if "action_frames" not in session_state:
            session_state["action_frames"] = 0
            
        challenge_passed = session_state.get("challenge_passed", False)
        
        if challenge_passed:
            response["challenge_passed"] = True
            response["progress"] = 100
            if response["is_matched"]:
                response["message"] = f"Face Verified ({response['match_pct']}%)! Ready to cast vote."
            else:
                response["message"] = f"Liveness passed, but face does not match profile ({response['match_pct']}%)."
            response["session_state"] = session_state
            return response
            
        # 3. Process Specific Challenge
        if challenge_type == "BLINK":
            # Detect blink transitions
            EAR_THRESHOLD = 0.20
            if avg_ear < EAR_THRESHOLD:
                session_state["eye_closed"] = True
            else:
                if session_state.get("eye_closed", False):
                    session_state["blinks"] += 1
                    session_state["eye_closed"] = False
                    
            blinks = session_state["blinks"]
            response["progress"] = min(100, int((blinks / 2.0) * 100))
            if blinks >= 2:
                session_state["challenge_passed"] = True
                challenge_passed = True
                response["message"] = "Blink challenge completed!"
            elif blinks == 1:
                response["message"] = "1 blink detected! Blink once more."
            else:
                response["message"] = "Action required: Please blink your eyes twice."
                
        elif challenge_type == "HEAD_LEFT":
            # Note: Webcam is typically mirrored. solvePnP yaw:
            # Turning head to user's left generates positive or negative yaw depending on camera view.
            # We check if yaw exceeds threshold in either mirrored direction or landmark ratio
            # Nose landmark 1 x vs center of ears 234 and 454
            nose_x = landmarks[1].x
            ear_l_x = landmarks[234].x
            ear_r_x = landmarks[454].x
            ratio = (nose_x - min(ear_l_x, ear_r_x)) / max(0.001, abs(ear_r_x - ear_l_x))
            
            # Left turn condition: yaw > 14 or yaw < -14 or ratio < 0.38
            is_turned_left = (yaw > 14.0) or (ratio < 0.38)
            
            if is_turned_left:
                session_state["action_frames"] += 1
                response["progress"] = min(100, int((session_state["action_frames"] / 4.0) * 100))
                if session_state["action_frames"] >= 4:
                    session_state["challenge_passed"] = True
                    challenge_passed = True
                    response["message"] = "Head turn left detected!"
                else:
                    response["message"] = "Hold head turned left..."
            else:
                response["progress"] = 0
                response["message"] = "Action required: Please turn your head to the LEFT."
                
        elif challenge_type == "HEAD_RIGHT":
            nose_x = landmarks[1].x
            ear_l_x = landmarks[234].x
            ear_r_x = landmarks[454].x
            ratio = (nose_x - min(ear_l_x, ear_r_x)) / max(0.001, abs(ear_r_x - ear_l_x))
            
            is_turned_right = (yaw < -14.0) or (ratio > 0.62)
            
            if is_turned_right:
                session_state["action_frames"] += 1
                response["progress"] = min(100, int((session_state["action_frames"] / 4.0) * 100))
                if session_state["action_frames"] >= 4:
                    session_state["challenge_passed"] = True
                    challenge_passed = True
                    response["message"] = "Head turn right detected!"
                else:
                    response["message"] = "Hold head turned right..."
            else:
                response["progress"] = 0
                response["message"] = "Action required: Please turn your head to the RIGHT."
                
        elif challenge_type == "SMILE":
            # Smile threshold: normal is ~0.35 - 0.40, smile is > 0.45
            is_smiling = smile_ratio > 0.44
            if is_smiling:
                session_state["action_frames"] += 1
                response["progress"] = min(100, int((session_state["action_frames"] / 4.0) * 100))
                if session_state["action_frames"] >= 4:
                    session_state["challenge_passed"] = True
                    challenge_passed = True
                    response["message"] = "Smile verified!"
                else:
                    response["message"] = "Keep smiling..."
            else:
                response["progress"] = 0
                response["message"] = "Action required: Please smile at the camera."
        else:
            # Fallback direct face match challenge
            session_state["challenge_passed"] = True
            challenge_passed = True
            response["message"] = "Looking directly at camera."
            
        response["challenge_passed"] = challenge_passed
        if challenge_passed and response["is_matched"]:
            response["message"] = f"Identity Verified ({response['match_pct']}%)! Challenge Passed."
            response["progress"] = 100
        elif challenge_passed and not response["is_matched"]:
            response["message"] = f"Liveness Passed, but face match low ({response['match_pct']}%). Look closely at camera."
            
        response["session_state"] = session_state
        return response
