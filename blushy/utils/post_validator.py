from beam import env
from ultralytics import YOLO
import numpy as np
import random
from google.oauth2 import service_account
from icecream import ic
from blushy.utils.siglip_manager import SiglipManager
from blushy.utils.base import url_to_pil_image


PATH= "/Users/tolgagunduz/Documents/projects/blushyv2/model-weigths"

if env.is_remote():
    PATH= "/volumes/model-weights"




class PostValidator:
    def __init__(self):
        self.model = YOLO(f"{PATH}/yolo11n-pose.pt")  # pretrained YOLO11n model
        self.siglip_manager=SiglipManager()

    def check_pose_requirements(self,keypoints, confidence_threshold=0.5):
        """
        Check if eyes are visible and upper legs are detected
        
        Args:
            keypoints: Pose keypoints from YOLO (shape: Nx3 where N is number of keypoints)
            confidence_threshold: Minimum confidence score to consider keypoint visible
        
        Returns:
            dict: Status of different body parts visibility
        """
    
        # YOLO keypoint indices
        LEFT_EYE = 3
        RIGHT_EYE = 4
        LEFT_HIP = 11
        RIGHT_HIP = 12
        LEFT_KNEE = 13
        RIGHT_KNEE = 14

        #ic(keypoints)

        # Check eyes visibility
        eyes_visible = (keypoints[LEFT_EYE][0] > 0 or 
                    keypoints[RIGHT_EYE][0] > 0)

        # Check upper legs (thighs) visibility
        # Upper legs are visible if both hips and knees are detected
        upper_legs_visible = (
            keypoints[LEFT_HIP][0] > 0 or
            keypoints[RIGHT_HIP][0] > 0 and
            keypoints[LEFT_KNEE][0] > 0 or
            keypoints[RIGHT_KNEE][0] > 0
        )

        return eyes_visible and upper_legs_visible
    


    def is_person_straight(self,keypoints, threshold_angle=30):
        """
        Determine if a person is standing straight using YOLO keypoints
        
        Args:
            keypoints: Pose keypoints from YOLO
            threshold_angle: Maximum allowed angle deviation from vertical (degrees)
        
        Returns:
            bool: True if person is standing straight, False otherwise
        """
        # Get relevant keypoints for posture analysis
        # Using shoulders, hips, and ankles
        left_shoulder = keypoints[5]
        right_shoulder = keypoints[6]
        left_hip = keypoints[11]
        right_hip = keypoints[12]
        left_ankle = keypoints[15]
        right_ankle = keypoints[16]

        # Calculate midpoints
        shoulder_midpoint = np.mean([left_shoulder, right_shoulder], axis=0)
        hip_midpoint = np.mean([left_hip, right_hip], axis=0)
        ankle_midpoint = np.mean([left_ankle, right_ankle], axis=0)

        # Calculate angle between vertical line and body line
        vertical_vector = np.array([0, -1])  # Pointing up
        body_vector = shoulder_midpoint - ankle_midpoint
        body_vector = body_vector / np.linalg.norm(body_vector)

        angle = np.arccos(np.dot(vertical_vector, body_vector))
        angle_degrees = np.degrees(angle)

        return angle_degrees <= threshold_angle


    def validate_post(self,image_source):
        
        results = self.model(image_source)
        num_people = len(results[0].boxes)
        print("number of people",num_people)
        if num_people != 1:
            return False
        keypoints=results[0].keypoints.xy.numpy()[0]
        #ic(keypoints)
        is_pose_right=self.check_pose_requirements(keypoints)
        is_pose_straight=self.is_person_straight(keypoints)
        print("right pose",is_pose_right,"straight pose",is_pose_straight)
        return is_pose_right and is_pose_straight and self.is_adult_person(image_source) and self.is_women(image_source)
    
    def is_adult_person(self,image_source):
        if isinstance(image_source,str):
            image_source = url_to_pil_image(image_source)
        result=self.siglip_manager.classify(image_source,["woman","man","child"])
        print(result)
        return result[0][0]>0.5
    
    def is_women(self,image_source):
        if isinstance(image_source,str):
            image_source = url_to_pil_image(image_source)
        result=self.siglip_manager.classify(image_source,["female","male"])
        return result[0][0]>result[0][1]
    
    def is_men(self,image_source):
        if isinstance(image_source,str):
            image_source = url_to_pil_image(image_source)
        result=self.siglip_manager.classify(image_source,["male","female"])
        return result[0][0]>result[0][1] and result[0][0]>0.9
    