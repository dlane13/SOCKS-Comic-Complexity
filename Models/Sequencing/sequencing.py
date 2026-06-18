import ollama
from pathlib import Path

IMAGES_PATH = Path('/Users/darbylane/Library/CloudStorage/OneDrive-UniversityofVermont/'
                   'VEA study - tasks for students/SOCKS project/CH Corpus/Originals')

response = ollama.chat(
    model="qwen2.5vl:7b",
    messages=[{
        "role": "user",
        "content": "Consider the following: Shifts in time maintaining full views of scenes are simpler than those that shift between views of characters, between viewpoints (i.e., zooms), between different perspectives (e.g., third to first person point-of-view), between different domains (e.g., from “reality” to a dream sequence or flashback), or that use idiosyncratic sequencing patterns (e.g., “cross-cutting” shifts back and forth between characters). Given this information, describe the complexity of the sequencing of images in the comic, and rate it overall on a scale of 0-1, with 0 being the simplest and 1 being the most complex.",
        "images": [IMAGES_PATH / 'CH.1985.11.18.png']
    }]
)
print(response.message.content)