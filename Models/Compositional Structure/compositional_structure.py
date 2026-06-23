import ollama
from pathlib import Path

IMAGES_PATH = Path('/Users/darbylane/Library/CloudStorage/OneDrive-UniversityofVermont/'
                   'VEA study - tasks for students/SOCKS project/CH Corpus/Originals')

PROMPT = "Consider the following: Comic panels vary in how they depict information, such as the angle of viewpoint (lateral, high/low angles), shot scale (long shot to close up), or framing angle (straight or tilted content). More normative compositions (lateral angles, full shots, straight content) are considered easier to comprehend than more deviant compositions. Given this information, describe the complexity of the compositional structure of the comic, and rate it overall on a scale of 0-1, with 0 being the simplest and 1 being the most complex."

response = ollama.chat(
    model="qwen2.5vl:7b",
    messages=[{
        "role": "user",
        "content": PROMPT,
        "images": [IMAGES_PATH / 'CH.1985.11.27.png']
    }]
)
print(f"SIMPLE RESPONSE \n ----------------------------- \n {response.message.content} \n ----------------------------")

response = ollama.chat(
    model="qwen2.5vl:7b",
    messages=[{
        "role": "user",
        "content": PROMPT,
        "images": [IMAGES_PATH / 'CH.1985.11.29.png']
    }]
)
print(f"COMPLEX RESPONSE \n ----------------------------- \n {response.message.content} \n ----------------------------")