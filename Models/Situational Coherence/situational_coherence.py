import ollama
from pathlib import Path

IMAGES_PATH = Path('/Users/darbylane/Library/CloudStorage/OneDrive-UniversityofVermont/'
                   'VEA study - tasks for students/SOCKS project/CH Corpus/Originals')

response = ollama.chat(
    model="qwen2.5vl:7b",
    messages=[{
        "role": "user",
        "content": "Consider the following: Greater shifts between panels in various meaningful dimensions (e.g., time, spatial location, characters) will be harder to comprehend than fewer shifts. Given this information, describe the complexity of the situational coherence of the comic, and rate it overall on a scale of 0-1, with 0 being the simplest and 1 being the most complex.",
        "images": [IMAGES_PATH / 'CH.1985.11.18.png']
    }]
)
print(response.message.content)