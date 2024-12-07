import os
import subprocess
from dataclasses import dataclass
from typing import Any

import numpy as np
import supervision as sv
import torch
from blushy.utils.siglip_manager import SiglipManager
from PIL import Image as PILImage

from autodistill.detection import CaptionOntology, DetectionBaseModel
from autodistill.helpers import load_image
from blushy.utils.base import url_to_pil_image
HOME = os.path.expanduser("~")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


@dataclass
class OWLv2(DetectionBaseModel):
    ontology: CaptionOntology

    def get_largest_bbox(self,results):
        # Get all detections for the specified class
        class_detections = results[results.class_id == 0]  # Assuming class_id 0 corresponds to our target class
        
        if len(class_detections) == 0:
            return None
        
        # Calculate areas of all bounding boxes
        areas = (class_detections.xyxy[:, 2] - class_detections.xyxy[:, 0]) * \
                (class_detections.xyxy[:, 3] - class_detections.xyxy[:, 1])
        
        # Get the index of the largest box
        largest_idx = np.argmax(areas)
        
        # Create new results with only the largest box
        largest_detection = class_detections[largest_idx:largest_idx+1]
        
        return largest_detection

    def __init__(self,processor=None,model=None,siglip_manager:SiglipManager=None):
        # install transformers from source, since OWLv2 is not yet in a release
        # (as of October 26th, 2023)
        try:
            from transformers import Owlv2ForObjectDetection, Owlv2Processor
        except:
            subprocess.run(
                ["pip3", "install", "git+https://github.com/huggingface/transformers"]
            )
            from transformers import Owlv2ForObjectDetection, Owlv2Processor

        if processor:
            self.processor=processor
        else:
            self.processor = Owlv2Processor.from_pretrained(
            "google/owlv2-base-patch16-ensemble"
        )

        if model:
            self.model=model
        else:
            self.model = Owlv2ForObjectDetection.from_pretrained(
            "google/owlv2-base-patch16-ensemble"
        )
        self.siglip_manager=siglip_manager
        

    def predict(self, input: Any, confidence: int = 0.1) -> sv.Detections:
        image = load_image(input, return_format="PIL")
        texts = [self.ontology.prompts()]

        inputs = self.processor(text=texts, images=image, return_tensors="pt")
        outputs = self.model(**inputs)

        target_sizes = torch.Tensor([image.size[::-1]])

        results = self.processor.post_process_object_detection(
            outputs=outputs, target_sizes=target_sizes, threshold=0.1
        )

        i = 0
        text = texts[i]

        boxes, scores, labels = (
            results[i]["boxes"],
            results[i]["scores"],
            results[i]["labels"],
        )

        final_boxes, final_scores, final_labels = [], [], []

        for box, score, label in zip(boxes, scores, labels):
            box = [round(i, 2) for i in box.tolist()]

            if score < confidence:
                continue

            final_boxes.append(box)
            final_scores.append(score.item())
            final_labels.append(label.item())

        if len(final_boxes) == 0:
            return sv.Detections.empty()

        return sv.Detections(
            xyxy=np.array(final_boxes),
            class_id=np.array(final_labels),
            confidence=np.array(final_scores),
        )
    
    def get_bbox(self,classname:str,image_source:Any):
        self.ontology= CaptionOntology({classname: classname})
        results=self.predict(image_source)
        results= self.get_largest_bbox(results)
        if results:
            return results.xyxy[0]
        return None
    
    def get_embeddings(self,classname:str,image_source:Any):
        if not self.siglip_manager:
            self.siglip_manager=SiglipManager()
        if isinstance(image_source,str):
            image_source=url_to_pil_image(image_source)
        results= self.get_bbox(classname,image_source)
        print(results)
        if results is not None and isinstance(results, np.ndarray):
            image=image_source.crop(results)
            return self.siglip_manager.get_embeddings(image)
        return None

if __name__ == "__main__":
    owlv2=OWLv2()
    print(owlv2.get_embeddings("person","https://storage.googleapis.com/blushy-posts-maidentech/c2b16a3fd4ee4ca7724fb8b59f4e20f4572f5118310695657c50021f38bf52c0.jpg"))