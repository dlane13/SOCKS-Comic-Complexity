from transformers import AutoModel
from transformers import AutoTokenizer, AutoModelForMaskedLM
import numpy as np
from PIL import Image
from pathlib import Path
import torch
import os
from tensorflow.keras.utils import load_img, img_to_array
from chandra.model import InferenceManager
from chandra.model.schema import BatchInputItem
from PIL import Image
from transformers import AutoModelForImageTextToText, AutoProcessor
from chandra.model.hf import generate_hf
from chandra.model.schema import BatchInputItem
from chandra.output import parse_markdown
from PIL import Image
import torch

IMAGES_PATH = Path('/Users/darbylane/Library/CloudStorage/OneDrive-UniversityofVermont/'
                   'VEA study - tasks for students/SOCKS project/CH Corpus/Originals')
IMG_SIZE = (224, 224)

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

def tesseract_transcription():
    def extract_text_from_image(image_path):
        try:
            # 2. Load the image using OpenCV
            image = cv2.imread(image_path)
            if image is None:
                raise FileNotFoundError(f"Could not find or open the image at {image_path}")

            # 3. Preprocess the image (Crucial for Tesseract accuracy)
            # Convert to Grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Thresholding (converts to stark black and white)
            threshold_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

            # 4. Run Tesseract OCR on the processed image
            # --psm 3: Fully automatic page segmentation, but no OSD (Default)
            custom_config = r'--oem 1 --psm 3'
            extracted_text = pytesseract.image_to_string(threshold_img, config=custom_config)

            return extracted_text

        except Exception as e:
            return f"An error occurred: {str(e)}"

    # Example Usage:
    if __name__ == "__main__":
        images = []
        directory = IMAGES_PATH

        for path in directory.iterdir():
            if path.is_file():
                images.append(path.name)
        # Replace with your actual image path (png, jpg, tiff)
        # for image in images:

        #     sample_image = IMAGES_PATH / image 
            
        #     print("--- Extracting Text ---")
        #     text = extract_text_from_image(sample_image)
        #     print(text)
        sample_image = IMAGES_PATH / 'CH.1985.11.18.png'
        text = extract_text_from_image(sample_image)
        print(text)
        img = Image.open(Path(IMAGES_PATH / 'CH.1985.11.18.png'))
        img.show()

# def paddleocr_transcription():
#     # Initialize the OCR engine
#     # use_angle_cls=True handles rotated text
#     # lang='en' specifies the language model
#     ocr = PaddleOCR(use_angle_cls=True, lang='en')

#     # Define the path to your image
#     image_path = IMAGES_PATH / 'CH.1985.11.18.png'

#     def load_image(filepath: Path) -> np.ndarray:
#         img = load_img(filepath, target_size=IMG_SIZE)
#         arr = img_to_array(img) / 255.0
#         return arr

#     # Run the OCR engine
#     result = ocr.ocr(load_image(image_path))

#     # Parse and display the extracted text
#     for idx in range(len(result)):
#         res = result[idx]
#         for line in res:
#             detected_text = line[1][0]
#             confidence_score = line[1][1]
#             print(f"Text: {detected_text} | Confidence: {confidence_score:.2f}")

#     img = Image.open(Path(IMAGES_PATH / 'CH.1985.11.18.png'))
#     img.show()

def chandra_ocr_transcription():
    model = AutoModelForImageTextToText.from_pretrained(
        "datalab-to/chandra-ocr-2",
        dtype=torch.bfloat16,
        device_map="auto",
    )
    model.eval()
    model.processor = AutoProcessor.from_pretrained("datalab-to/chandra-ocr-2")
    model.processor.tokenizer.padding_side = "left"

    batch = [
        BatchInputItem(
            image=Image.open(Path(IMAGES_PATH / 'CH.1985.11.18.png')),
            prompt_type="ocr_layout",
            prompt="Only transcribe the text from the image, and do not describe anything additional about the scene or the characters or events."
        )
    ]

    result = generate_hf(batch, model)[0]
    markdown = parse_markdown(result.raw)
    print(markdown)
    return markdown



lexical_complexity(chandra_ocr_transcription())


