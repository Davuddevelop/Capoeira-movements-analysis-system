"""
Pose Detector Module

This module handles video processing and pose detection using Google MediaPipe.
It processes videos frame by frame, extracts body landmarks, and can draw
skeleton overlays for visualization.

MediaPipe Pose provides 33 body landmarks that we use to calculate joint angles
for capoeira movement analysis.
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import List, Dict, Optional, Tuple, Generator
from dataclasses import dataclass, field
from pathlib import Path
import time


@dataclass
class FrameResult:
    """Stores the analysis results for a single video frame."""
    frame_number: int
    timestamp: float  # Timestamp in seconds
    landmarks: Optional[object] = None  # MediaPipe landmarks
    landmarks_list: List[Dict] = field(default_factory=list)  # Converted to list of dicts
    pose_detected: bool = False
    annotated_frame: Optional[np.ndarray] = None


@dataclass
class VideoInfo:
    """Stores metadata about the processed video."""
    path: str
    width: int
    height: int
    fps: float
    total_frames: int
    duration: float  # Duration in seconds


class PoseDetector:
    """
    Detects body poses in video files using MediaPipe Pose.

    This class processes videos frame by frame, extracts the 33 body landmarks
    from MediaPipe, and can generate annotated videos with skeleton overlays.

    Attributes:
        min_detection_confidence: Minimum confidence for initial detection
        min_tracking_confidence: Minimum confidence for tracking between frames
        model_complexity: 0, 1, or 2. Higher = more accurate but slower
    """

    def __init__(self,
                 min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5,
                 model_complexity: int = 1):
        """
        Initialize the pose detector.

        Args:
            min_detection_confidence: Confidence threshold for pose detection (0-1)
            min_tracking_confidence: Confidence threshold for pose tracking (0-1)
            model_complexity: Model complexity (0=lite, 1=full, 2=heavy)
        """
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.model_complexity = model_complexity

        # MediaPipe components (Tasks API)
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision
        
        self.python_tasks = python
        self.vision_tasks = vision
        
        # Landmarker instance
        self._landmarker = None
        
        # Model path
        self.model_path = str(Path(__file__).parent / "models" / "pose_landmarker.task")

    def _create_landmarker_instance(self):
        """Create a new MediaPipe Pose Landmarker instance."""
        base_options = self.python_tasks.BaseOptions(model_asset_path=self.model_path)
        options = self.vision_tasks.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=self.vision_tasks.RunningMode.VIDEO,
            num_poses=1,
            min_pose_detection_confidence=self.min_detection_confidence,
            min_pose_presence_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence,
            output_segmentation_masks=False
        )
        return self.vision_tasks.PoseLandmarker.create_from_options(options)

    def _landmarks_to_list(self, landmarks_list) -> List[Dict]:
        """
        Convert Tasks API landmarks to a list of dictionaries.
        """
        if not landmarks_list:
            return []

        return [
            {
                'x': lm.x,
                'y': lm.y,
                'z': lm.z,
                'visibility': getattr(lm, 'visibility', 0.0)
            }
            for lm in landmarks_list
        ]

    def _draw_skeleton(self, frame: np.ndarray, landmarks_list: List) -> np.ndarray:
        """Draw skeleton manually since solutions.drawing_utils is missing."""
        annotated = frame.copy()
        h, w, _ = frame.shape
        
        # Connections definition (standard MediaPipe Pose)
        connections = [
            (11, 12), (11, 13), (13, 15), (12, 14), (14, 16), # Upper body
            (11, 23), (12, 24), (23, 24), # Torso
            (23, 25), (25, 27), (27, 31), (24, 26), (26, 28), (28, 32) # Lower body
        ]
        
        # Draw connections
        for start_idx, end_idx in connections:
            if start_idx < len(landmarks_list) and end_idx < len(landmarks_list):
                start_lm = landmarks_list[start_idx]
                end_lm = landmarks_list[end_idx]
                
                start_point = (int(start_lm.x * w), int(start_lm.y * h))
                end_point = (int(end_lm.x * w), int(end_lm.y * h))
                
                cv2.line(annotated, start_point, end_point, (255, 255, 255), 2)
        
        # Draw landmarks
        for lm in landmarks_list:
            point = (int(lm.x * w), int(lm.y * h))
            cv2.circle(annotated, point, 3, (0, 255, 0), -1)
            
        return annotated

    def get_video_info(self, video_path: str) -> 'VideoInfo':
        """Get metadata about a video file."""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        cap.release()

        return VideoInfo(
            path=video_path,
            width=width,
            height=height,
            fps=fps,
            total_frames=total_frames,
            duration=duration
        )

    def process_frame(self, frame: np.ndarray, frame_number: int,
                     timestamp: float, draw_skeleton: bool = True) -> FrameResult:
        """Process a single frame using Tasks API."""
        if self._landmarker is None:
            self._landmarker = self._create_landmarker_instance()

        result = FrameResult(frame_number=frame_number, timestamp=timestamp)
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Process the frame for video mode
        # timestamp_ms must be monotonically increasing
        timestamp_ms = int(timestamp * 1000)
        detection_result = self._landmarker.detect_for_video(mp_image, timestamp_ms)
        
        if detection_result.pose_landmarks:
            # We take the first detected pose
            pose_landmarks = detection_result.pose_landmarks[0]
            result.pose_detected = True
            
            # To maintain compatibility with code expecting .landmark attribute
            class MockLandmarks:
                def __init__(self, lms): self.landmark = lms
            result.landmarks = MockLandmarks(pose_landmarks)
            
            result.landmarks_list = self._landmarks_to_list(pose_landmarks)
            
            if draw_skeleton:
                result.annotated_frame = self._draw_skeleton(frame, pose_landmarks)
            else:
                result.annotated_frame = frame.copy()
        else:
            result.annotated_frame = frame.copy() if draw_skeleton else None
            
        return result

    def process_video(self, video_path: str,
                     draw_skeleton: bool = True,
                     progress_callback=None) -> Generator[FrameResult, None, None]:
        """Process a video file and yield results."""
        if not Path(video_path).exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        video_info = self.get_video_info(video_path)
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")

        # Create landmarker instance for this session
        self._landmarker = self._create_landmarker_instance()

        try:
            frame_number = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                timestamp = frame_number / video_info.fps if video_info.fps > 0 else 0
                result = self.process_frame(frame, frame_number, timestamp, draw_skeleton)

                if progress_callback:
                    progress_callback(frame_number, video_info.total_frames)

                yield result
                frame_number += 1
        finally:
            cap.release()
            if self._landmarker:
                self._landmarker.close()
                self._landmarker = None

    def process_video_to_list(self, video_path: str,
                              draw_skeleton: bool = True,
                              progress_callback=None) -> Tuple[List[FrameResult], VideoInfo]:
        """
        Process a video file and return all results as a list.

        This loads all frame results into memory. Use process_video() generator
        for memory-efficient processing of long videos.

        Args:
            video_path: Path to the video file
            draw_skeleton: Whether to draw skeleton overlay on frames
            progress_callback: Optional callback function(current_frame, total_frames)

        Returns:
            Tuple of (list of FrameResults, VideoInfo)
        """
        video_info = self.get_video_info(video_path)
        results = list(self.process_video(video_path, draw_skeleton, progress_callback))
        return results, video_info

    def save_annotated_video(self, video_path: str, output_path: str,
                            progress_callback=None) -> str:
        """
        Process a video and save an annotated version with skeleton overlay.

        Args:
            video_path: Path to the input video
            output_path: Path for the output annotated video
            progress_callback: Optional callback function(current_frame, total_frames)

        Returns:
            Path to the saved annotated video
        """
        video_info = self.get_video_info(video_path)

        # Set up video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(
            output_path,
            fourcc,
            video_info.fps,
            (video_info.width, video_info.height)
        )

        if not out.isOpened():
            raise ValueError(f"Could not create output video: {output_path}")

        try:
            for result in self.process_video(video_path, draw_skeleton=True,
                                            progress_callback=progress_callback):
                if result.annotated_frame is not None:
                    out.write(result.annotated_frame)

        finally:
            out.release()

        return output_path

    def detect_pose_in_image(self, image_path: str,
                            draw_skeleton: bool = True) -> FrameResult:
        """Process a single image using Tasks API."""
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")

        # For static images, we use the same landmarker but it works fine 
        # (Alternatively we could use IMAGE mode, but VIDEO mode with timestamp 0 is OK)
        result = self.process_frame(image, 0, 0.0, draw_skeleton)
        return result

    def get_landmark_names(self) -> List[str]:
        """
        Get the list of MediaPipe pose landmark names.

        Returns:
            List of landmark names in order (0-32)
        """
        return [
            'nose', 'left_eye_inner', 'left_eye', 'left_eye_outer',
            'right_eye_inner', 'right_eye', 'right_eye_outer',
            'left_ear', 'right_ear', 'mouth_left', 'mouth_right',
            'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
            'left_wrist', 'right_wrist', 'left_pinky', 'right_pinky',
            'left_index', 'right_index', 'left_thumb', 'right_thumb',
            'left_hip', 'right_hip', 'left_knee', 'right_knee',
            'left_ankle', 'right_ankle', 'left_heel', 'right_heel',
            'left_foot_index', 'right_foot_index'
        ]


def get_detection_stats(results: List[FrameResult]) -> Dict:
    """
    Calculate detection statistics from a list of frame results.

    Args:
        results: List of FrameResult objects

    Returns:
        Dictionary with detection statistics
    """
    total_frames = len(results)
    detected_frames = sum(1 for r in results if r.pose_detected)

    return {
        'total_frames': total_frames,
        'detected_frames': detected_frames,
        'missed_frames': total_frames - detected_frames,
        'detection_rate': detected_frames / total_frames if total_frames > 0 else 0,
        'detection_percentage': (detected_frames / total_frames * 100) if total_frames > 0 else 0
    }
