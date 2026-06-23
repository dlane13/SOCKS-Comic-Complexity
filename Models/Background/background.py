import ollama
from pathlib import Path

IMAGES_PATH = Path('/Users/darbylane/Library/CloudStorage/OneDrive-UniversityofVermont/'
                   'VEA study - tasks for students/SOCKS project/CH Corpus/Originals')

response = ollama.chat(
    model="qwen2.5vl:7b",
    messages=[{
        "role": "user",
        "content": "Consider the following: Depicted backgrounds clearly show the spatial location and are easiest to comprehend relative to those with symbolic content or absent or impossible backgrounds. Given this information, describe the complexity of the comic, and rate it overall on a scale of 0-1, with 0 being the simplest and 1 being the most complex. Ignore the text bubbles, and study only the background of the image when assigning this score and interpreting the comic.",
        "images": [IMAGES_PATH / 'CH.1985.11.27.png']
    }]
)
print(response.message.content)

response = ollama.chat(
    model="qwen2.5vl:7b",
    messages=[{
        "role": "user",
        "content": "Consider the following: Depicted backgrounds clearly show the spatial location and are easiest to comprehend relative to those with symbolic content or absent or impossible backgrounds. Given this information, describe the complexity of the comic, and rate it overall on a scale of 0-1, with 0 being the simplest and 1 being the most complex. Ignore the text bubbles, and study only the background of the image when assigning this score and interpreting the comic.",
        "images": [IMAGES_PATH / 'CH.1985.11.29.png']
    }]
)
print(response.message.content)