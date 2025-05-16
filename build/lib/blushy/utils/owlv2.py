import os
import subprocess
from dataclasses import dataclass
from typing import Any, List

import numpy as np
import supervision as sv
import torch
from blushy.utils.siglip_manager import SiglipManager,ImageEmbeddingManager
from PIL import Image as PILImage
from transformers import Owlv2ForObjectDetection, Owlv2Processor
from autodistill.detection import CaptionOntology, DetectionBaseModel
from autodistill.helpers import load_image
from blushy.utils.base import url_to_pil_image
HOME = os.path.expanduser("~")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


@dataclass
class OWLv2(DetectionBaseModel):
    ontology: CaptionOntology

    @staticmethod
    def _crop_image_by_box_static(image: PILImage.Image, box: List[int], ratio: float = 1.0) -> PILImage.Image:
        """
        Crops an image centered on a bounding box to a specific aspect ratio (height/width).
        The crop will be large enough to contain the original box.

        Args:
            image (PILImage.Image): The input PIL image.
            box (List[int]): The bounding box [xmin, ymin, xmax, ymax].
            ratio (float): The target aspect ratio (height / width) for the crop.
                           Defaults to 1.0 (square crop).

        Returns:
            PILImage.Image: The cropped PIL image.
        """
        if ratio <= 0:
            raise ValueError("Ratio (height/width) must be positive.")

        img_width, img_height = image.size
        xmin, ymin, xmax, ymax = map(int, box) # Ensure integer coords for box

        # Clamp original box to image bounds just in case
        xmin = max(0, xmin)
        ymin = max(0, ymin)
        xmax = min(img_width, xmax)
        ymax = min(img_height, ymax)

        box_width = xmax - xmin
        box_height = ymax - ymin

        if box_width <= 0 or box_height <= 0:
             print(f"Warning: Invalid bounding box received: {box}. Returning original image.")
             return image # Or raise an error

        center_x = xmin + box_width / 2
        center_y = ymin + box_height / 2

        # Determine the dimensions of the new crop box based on the target aspect ratio
        # Ensure the new box contains the original box
        if box_height / box_width > ratio:
            # Box is taller than target ratio; height determines the size
            new_height = float(box_height)
            new_width = new_height / ratio
        else:
            # Box is wider than or equal to target ratio; width determines the size
            new_width = float(box_width)
            new_height = new_width * ratio

        # Calculate crop coordinates centered on the original box's center
        new_xmin = center_x - new_width / 2
        new_ymin = center_y - new_height / 2
        new_xmax = center_x + new_width / 2
        new_ymax = center_y + new_height / 2

        # Clamp crop coordinates to image boundaries
        final_xmin = max(0, int(round(new_xmin)))
        final_ymin = max(0, int(round(new_ymin)))
        final_xmax = min(img_width, int(round(new_xmax)))
        final_ymax = min(img_height, int(round(new_ymax)))

        # Ensure final coordinates are valid
        if final_xmin >= final_xmax or final_ymin >= final_ymax:
             print(f"Warning: Calculated crop box is invalid ({final_xmin}, {final_ymin}, {final_xmax}, {final_ymax}). Returning original image.")
             return image # Or crop the original box? Returning original seems safer.

        cropped_image = image.crop((final_xmin, final_ymin, final_xmax, final_ymax))
        return cropped_image

    def crop_image_by_word(self, image_source: Any, word: str, ratio: float = 1.0) -> PILImage.Image:
        """
        Detects a word in an image, finds its largest bounding box, and crops the image
        around that box, expanded by a given ratio.

        Args:
            image (PILImage.Image): The input PIL image.
            word (str): The word to detect in the image.
            ratio (float): The ratio to expand the bounding box dimensions by.
                           Defaults to 1.0 (no expansion).

        Returns:
            PILImage.Image: The cropped PIL image, or the original image if the word is not found.
        """

   
        # Perform prediction
        image_source=load_image(image_source,return_format="PIL")
        box=self.get_bbox(word,image_source)

        if box is None:
            print(f"Warning: Word '{word}' not found in the image. Returning original image.")
            return image_source

        # Crop using the static helper method
        return OWLv2._crop_image_by_box_static(image_source, box, ratio)
        


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
            self.siglip_manager=ImageEmbeddingManager()
        if isinstance(image_source,str):
            image_source=url_to_pil_image(image_source)
        results= self.get_bbox(classname,image_source)
        print(results)
        if results is not None and isinstance(results, np.ndarray):
            image=image_source.crop(results)
            return self.siglip_manager.get_embeddings(image)
        return None

if __name__ == "__main__":
    processor = Owlv2Processor.from_pretrained(
                "google/owlv2-base-patch16-ensemble"
            )

    model = Owlv2ForObjectDetection.from_pretrained(
                "google/owlv2-base-patch16-ensemble"
            )
    owlv2=OWLv2(processor,model)
    img=owlv2.crop_image_by_word("https://sky-static.mavi.com/MOBIL-KADIN-4-1-148241147.jpg","top",ratio=16/16)
    img.show()