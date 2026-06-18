import ollama
from pathlib import Path

IMAGES_PATH = Path('/Users/darbylane/Library/CloudStorage/OneDrive-UniversityofVermont/'
                   'VEA study - tasks for students/SOCKS project/CH Corpus/Originals')

response = ollama.chat(
    model="qwen2.5vl:7b",
    messages=[{
        "role": "user",
        "content": "Consider the following: “Macros” (panels depicting an entire scene) are more explicit in terms of semantic content, and should thus be easier to understand, compared to “monos” (panels depicting only one character or object) or “micros” (which show a “zoomed in” part of a character, object, or scene). Given this information, describe the complexity of the framing structure of the comic, and rate it overall on a scale of 0-1, with 0 being the simplest and 1 being the most complex.",
        "images": [IMAGES_PATH / 'CH.1985.11.18.png']
    }]
)
print(response.message.content)