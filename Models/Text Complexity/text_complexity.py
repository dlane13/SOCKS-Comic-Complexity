from transformers import AutoModel
from transformers import AutoTokenizer, AutoModelForMaskedLM
import numpy as np
from PIL import Image
from pathlib import Path
import torch
import os

IMAGES_PATH = Path('/Users/darbylane/Library/CloudStorage/OneDrive-UniversityofVermont/'
                   'VEA study - tasks for students/SOCKS project/CH Corpus/Originals')

def manga_whisperer_transcription():
    images = []
    directory = IMAGES_PATH
    
    for path in directory.iterdir():
        if path.is_file():
            images.append(path.name)

    def read_image_as_np_array(image_path):
        with open(IMAGES_PATH / image_path, "rb") as file:
            image = Image.open(file).convert("L").convert("RGB")
            image = np.array(image)
        return image

    images = [read_image_as_np_array(image) for image in images]

    model = AutoModel.from_pretrained("ragavsachdeva/magi", trust_remote_code=True).cuda()
    with torch.no_grad():
        results = model.predict_detections_and_associations(images)
        text_bboxes_for_all_images = [x["texts"] for x in results]
        ocr_results = model.predict_ocr(images, text_bboxes_for_all_images)

    for i in range(len(images)):
        model.visualise_single_image_prediction(images[i], results[i], filename=f"image_{i}.png")
        transcription = model.generate_transcript_for_single_image(results[i], ocr_results[i], filename=f"transcript_{i}.txt")
    
    return transcription

def lexical_complexity(transcription: str) -> int:
    tokenizer = AutoTokenizer.from_pretrained("abhi1nandy2/Bible-roberta-base")
    model = AutoModelForMaskedLM.from_pretrained("abhi1nandy2/Bible-roberta-base", trust_remote_code=True).cuda()
    inputs = tokenizer(transcription, return_tensors='pt')
    outputs = model.generate(**inputs)
    print(tokenizer.batch_decode(outputs))

lexical_complexity(manga_whisperer_transcription())