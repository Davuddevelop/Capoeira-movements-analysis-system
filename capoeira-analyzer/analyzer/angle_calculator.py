"""
Angle Calculator Module

This module provides functions to calculate joint angles from body landmarks.
It's the mathematical foundation of the movement analysis system.

The angles are calculated using the positions of three points:
- Point A: The starting joint
- Point B: The joint where the angle is measured (vertex)
- Point C: The ending joint

Example: To calculate elbow angle, use shoulder (A), elbow (B), wrist (C)
"""

import numpy as np
from typing import Tuple, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class LandmarkPoint:
    """Represents a single body landmark with coordinates and visibility."""
    x: float
    y: float
    z: float
    visibility: float


class AngleCalculator:
    """
    Calculates joint angles from MediaPipe pose landmarks.

    MediaPipe provides 33 body landmarks. This class extracts the relevant
    landmarks and calculates angles for capoeira movement analysis.
    """

    # MediaPipe Pose landmark indices
    # Reference: https://developers.google.com/mediapipe/solutions/vision/pose_landmarker
    LANDMARKS = {
        # Face landmarks (0-10) - not used for movement scoring
        'nose': 0,
        'left_eye_inner': 1,
        'left_eye': 2,
        'left_eye_outer': 3,
        'right_eye_inner': 4,
        'right_eye': 5,
        'right_eye_outer': 6,
        'left_ear': 7,
        'right_ear': 8,
        'mouth_left': 9,
        'mouth_right': 10,

        # Upper body landmarks (11-22)
        'left_shoulder': 11,
        'right_shoulder': 12,
        'left_elbow': 13,
        'right_elbow': 14,
        'left_wrist': 15,
        'right_wrist': 16,
        'left_pinky': 17,
        'right_pinky': 18,
        'left_index': 19,
        'right_index': 20,
        'left_thumb': 21,
        'right_thumb': 22,

        # Lower body landmarks (23-32)
        'left_hip': 23,
        'right_hip': 24,
        'left_knee': 25,
        'right_knee': 26,
        'left_ankle': 27,
        'right_ankle': 28,
        'left_heel': 29,
        'right_heel': 30,
        'left_foot_index': 31,
        'right_foot_index': 32,
    }

    def __init__(self, min_visibility: float = 0.5):
        """
        Initialize the angle calculator.

        Args:
            min_visibility: Minimum visibility threshold for a landmark to be
                           considered valid (0.0 to 1.0). Default is 0.5.
        """
        self.min_visibility = min_visibility

    @staticmethod
    def calculate_angle(a: Tuple[float, float],
                       b: Tuple[float, float],
                       c: Tuple[float, float]) -> float:
        """
        Calculate the angle at point B formed by points A-B-C.

        This is the core angle calculation function. It computes the angle
        at the vertex (point B) using the arctangent of the vectors.

        Args:
            a: Coordinates of point A (x, y)
            b: Coordinates of point B (x, y) - the vertex
            c: Coordinates of point C (x, y)

        Returns:
            Angle in degrees (0 to 180)
        """
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)

        # Calculate vectors from B to A and from B to C
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - \
                  np.arctan2(a[1] - b[1], a[0] - b[0])

        # Convert to degrees and ensure positive angle
        angle = np.abs(radians * 180.0 / np.pi)

        # Normalize to 0-180 range
        if angle > 180.0:
            angle = 360 - angle

        return angle

    @staticmethod
    def calculate_angle_3d(a: Tuple[float, float, float],
                          b: Tuple[float, float, float],
                          c: Tuple[float, float, float]) -> float:
        """
        Calculate the angle at point B in 3D space.

        Uses vector dot product for more accurate 3D angle calculation.

        Args:
            a: Coordinates of point A (x, y, z)
            b: Coordinates of point B (x, y, z) - the vertex
            c: Coordinates of point C (x, y, z)

        Returns:
            Angle in degrees (0 to 180)
        """
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)

        # Create vectors from B to A and from B to C
        ba = a - b
        bc = c - b

        # Calculate dot product and magnitudes
        dot_product = np.dot(ba, bc)
        magnitude_ba = np.linalg.norm(ba)
        magnitude_bc = np.linalg.norm(bc)

        # Avoid division by zero
        if magnitude_ba == 0 or magnitude_bc == 0:
            return 0.0

        # Calculate angle using dot product formula
        cos_angle = dot_product / (magnitude_ba * magnitude_bc)

        # Clamp to [-1, 1] to handle floating point errors
        cos_angle = np.clip(cos_angle, -1.0, 1.0)

        angle = np.arccos(cos_angle) * 180.0 / np.pi

        return angle

    def _get_landmark_coords(self, landmarks, landmark_name: str,
                            use_3d: bool = False) -> Optional[Tuple]:
        """
        Extract coordinates from a landmark by name.

        Args:
            landmarks: MediaPipe pose landmarks
            landmark_name: Name of the landmark (e.g., 'left_knee')
            use_3d: Whether to return 3D coordinates (x, y, z)

        Returns:
            Tuple of coordinates or None if landmark not visible enough
        """
        idx = self.LANDMARKS.get(landmark_name)
        if idx is None:
            return None

        landmark = landmarks[idx]

        # Check visibility threshold
        if landmark.visibility < self.min_visibility:
            return None

        if use_3d:
            return (landmark.x, landmark.y, landmark.z)
        return (landmark.x, landmark.y)

    def calculate_knee_angle(self, landmarks, side: str = 'left',
                            use_3d: bool = False) -> Optional[float]:
        """
        Calculate the knee angle (hip-knee-ankle).

        A straight leg has ~180 degrees. A fully bent knee might be ~40 degrees.

        Args:
            landmarks: MediaPipe pose landmarks
            side: 'left' or 'right'
            use_3d: Whether to use 3D calculation

        Returns:
            Knee angle in degrees or None if landmarks not visible
        """
        hip = self._get_landmark_coords(landmarks, f'{side}_hip', use_3d)
        knee = self._get_landmark_coords(landmarks, f'{side}_knee', use_3d)
        ankle = self._get_landmark_coords(landmarks, f'{side}_ankle', use_3d)

        if None in (hip, knee, ankle):
            return None

        if use_3d:
            return self.calculate_angle_3d(hip, knee, ankle)
        return self.calculate_angle(hip, knee, ankle)

    def calculate_hip_angle(self, landmarks, side: str = 'left',
                           use_3d: bool = False) -> Optional[float]:
        """
        Calculate the hip angle (shoulder-hip-knee).

        Standing straight has ~180 degrees. Lifting leg forward decreases the angle.

        Args:
            landmarks: MediaPipe pose landmarks
            side: 'left' or 'right'
            use_3d: Whether to use 3D calculation

        Returns:
            Hip angle in degrees or None if landmarks not visible
        """
        shoulder = self._get_landmark_coords(landmarks, f'{side}_shoulder', use_3d)
        hip = self._get_landmark_coords(landmarks, f'{side}_hip', use_3d)
        knee = self._get_landmark_coords(landmarks, f'{side}_knee', use_3d)

        if None in (shoulder, hip, knee):
            return None

        if use_3d:
            return self.calculate_angle_3d(shoulder, hip, knee)
        return self.calculate_angle(shoulder, hip, knee)

    def calculate_elbow_angle(self, landmarks, side: str = 'left',
                             use_3d: bool = False) -> Optional[float]:
        """
        Calculate the elbow angle (shoulder-elbow-wrist).

        A straight arm has ~180 degrees. A fully bent elbow might be ~30 degrees.

        Args:
            landmarks: MediaPipe pose landmarks
            side: 'left' or 'right'
            use_3d: Whether to use 3D calculation

        Returns:
            Elbow angle in degrees or None if landmarks not visible
        """
        shoulder = self._get_landmark_coords(landmarks, f'{side}_shoulder', use_3d)
        elbow = self._get_landmark_coords(landmarks, f'{side}_elbow', use_3d)
        wrist = self._get_landmark_coords(landmarks, f'{side}_wrist', use_3d)

        if None in (shoulder, elbow, wrist):
            return None

        if use_3d:
            return self.calculate_angle_3d(shoulder, elbow, wrist)
        return self.calculate_angle(shoulder, elbow, wrist)

    def calculate_shoulder_angle(self, landmarks, side: str = 'left',
                                 use_3d: bool = False) -> Optional[float]:
        """
        Calculate the shoulder angle (elbow-shoulder-hip).

        Arm at side has ~0-20 degrees. Arm raised overhead has ~180 degrees.

        Args:
            landmarks: MediaPipe pose landmarks
            side: 'left' or 'right'
            use_3d: Whether to use 3D calculation

        Returns:
            Shoulder angle in degrees or None if landmarks not visible
        """
        elbow = self._get_landmark_coords(landmarks, f'{side}_elbow', use_3d)
        shoulder = self._get_landmark_coords(landmarks, f'{side}_shoulder', use_3d)
        hip = self._get_landmark_coords(landmarks, f'{side}_hip', use_3d)

        if None in (elbow, shoulder, hip):
            return None

        if use_3d:
            return self.calculate_angle_3d(elbow, shoulder, hip)
        return self.calculate_angle(elbow, shoulder, hip)

    def calculate_spine_angle(self, landmarks, use_3d: bool = False) -> Optional[float]:
        """
        Calculate the spine/torso inclination angle.

        Uses the midpoint of shoulders and hips to determine torso angle
        relative to vertical. Standing straight is ~180 degrees.

        Args:
            landmarks: MediaPipe pose landmarks
            use_3d: Whether to use 3D calculation

        Returns:
            Spine angle in degrees or None if landmarks not visible
        """
        left_shoulder = self._get_landmark_coords(landmarks, 'left_shoulder', use_3d)
        right_shoulder = self._get_landmark_coords(landmarks, 'right_shoulder', use_3d)
        left_hip = self._get_landmark_coords(landmarks, 'left_hip', use_3d)
        right_hip = self._get_landmark_coords(landmarks, 'right_hip', use_3d)

        if None in (left_shoulder, right_shoulder, left_hip, right_hip):
            return None

        # Calculate midpoints
        if use_3d:
            mid_shoulder = tuple(np.mean([left_shoulder, right_shoulder], axis=0))
            mid_hip = tuple(np.mean([left_hip, right_hip], axis=0))
            # Create a vertical reference point above the hip
            vertical_ref = (mid_hip[0], mid_hip[1] - 1, mid_hip[2])
            return self.calculate_angle_3d(mid_shoulder, mid_hip, vertical_ref)
        else:
            mid_shoulder = tuple(np.mean([left_shoulder, right_shoulder], axis=0))
            mid_hip = tuple(np.mean([left_hip, right_hip], axis=0))
            # Create a vertical reference point above the hip (y decreases going up in image)
            vertical_ref = (mid_hip[0], mid_hip[1] - 1)
            return self.calculate_angle(mid_shoulder, mid_hip, vertical_ref)

    def calculate_ankle_angle(self, landmarks, side: str = 'left',
                             use_3d: bool = False) -> Optional[float]:
        """
        Calculate the ankle angle (knee-ankle-foot_index).

        This measures the dorsiflexion/plantarflexion of the ankle.

        Args:
            landmarks: MediaPipe pose landmarks
            side: 'left' or 'right'
            use_3d: Whether to use 3D calculation

        Returns:
            Ankle angle in degrees or None if landmarks not visible
        """
        knee = self._get_landmark_coords(landmarks, f'{side}_knee', use_3d)
        ankle = self._get_landmark_coords(landmarks, f'{side}_ankle', use_3d)
        foot = self._get_landmark_coords(landmarks, f'{side}_foot_index', use_3d)

        if None in (knee, ankle, foot):
            return None

        if use_3d:
            return self.calculate_angle_3d(knee, ankle, foot)
        return self.calculate_angle(knee, ankle, foot)

    def calculate_all_angles(self, landmarks, use_3d: bool = False) -> Dict[str, Optional[float]]:
        """
        Calculate all relevant joint angles from pose landmarks.

        This is the main function to call for getting all angles needed
        for movement scoring.

        Args:
            landmarks: MediaPipe pose landmarks
            use_3d: Whether to use 3D calculations

        Returns:
            Dictionary with all joint angles
        """
        return {
            # Knee angles
            'left_knee': self.calculate_knee_angle(landmarks, 'left', use_3d),
            'right_knee': self.calculate_knee_angle(landmarks, 'right', use_3d),

            # Hip angles
            'left_hip': self.calculate_hip_angle(landmarks, 'left', use_3d),
            'right_hip': self.calculate_hip_angle(landmarks, 'right', use_3d),

            # Elbow angles
            'left_elbow': self.calculate_elbow_angle(landmarks, 'left', use_3d),
            'right_elbow': self.calculate_elbow_angle(landmarks, 'right', use_3d),

            # Shoulder angles
            'left_shoulder': self.calculate_shoulder_angle(landmarks, 'left', use_3d),
            'right_shoulder': self.calculate_shoulder_angle(landmarks, 'right', use_3d),

            # Spine angle
            'spine': self.calculate_spine_angle(landmarks, use_3d),

            # Ankle angles
            'left_ankle': self.calculate_ankle_angle(landmarks, 'left', use_3d),
            'right_ankle': self.calculate_ankle_angle(landmarks, 'right', use_3d),
        }

    def get_angle_summary(self, angles: Dict[str, Optional[float]]) -> str:
        """
        Generate a human-readable summary of the calculated angles.

        Args:
            angles: Dictionary of angle names to values

        Returns:
            Formatted string with angle values
        """
        lines = ["Joint Angles Summary:", "-" * 30]

        for name, value in angles.items():
            if value is not None:
                lines.append(f"{name.replace('_', ' ').title()}: {value:.1f}°")
            else:
                lines.append(f"{name.replace('_', ' ').title()}: Not visible")

        return "\n".join(lines)


# Utility function for quick angle calculation
def quick_angle(a: Tuple[float, float],
                b: Tuple[float, float],
                c: Tuple[float, float]) -> float:
    """
    Quick utility function to calculate angle at point B.

    This is a standalone function for simple angle calculations
    without needing to instantiate the AngleCalculator class.

    Args:
        a: Point A coordinates (x, y)
        b: Point B coordinates (x, y) - vertex
        c: Point C coordinates (x, y)

    Returns:
        Angle in degrees
    """
    return AngleCalculator.calculate_angle(a, b, c)
