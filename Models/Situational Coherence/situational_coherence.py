import ollama
from pathlib import Path

IMAGES_PATH = Path('/Users/darbylane/Library/CloudStorage/OneDrive-UniversityofVermont/'
                   'VEA study - tasks for students/SOCKS project/CH Corpus/Originals')

PROMPT = "Consider the following: Greater shifts between panels in various meaningful dimensions (e.g., time, spatial location, characters) will be harder to comprehend than fewer shifts. Given this information, describe the complexity of the situational coherence of the provided Calvin and Hobbes comic, and rate it overall on a scale of 0-1, with 0 being the simplest and 1 being the most complex. Format the response in LaTeX."
PROMPT = "Consider the following description of situational coherence complexity in a comic: Greater shifts between panels in various meaningful dimensions - specifically time, spatial location/setting, and characters - will be harder to comprehend than fewer shifts. Given this information, describe the complexity of the situational coherence of the provided Calvin and Hobbes comic, and rate it overall on a scale of 0-1, with 0 being the simplest and 1 being the most complex. Format the response in LaTeX."
PROMPT = "Consider the following description of situational coherence complexity in a comic: Greater shifts between panels in various meaningful dimensions - specifically time, spatial location/setting, and characters - will be harder to comprehend than fewer shifts. Given this information, describe the complexity of the situational coherence of the provided Calvin and Hobbes comic for each of the provided dimensions, and rate it overall on a scale of 0-1, with 0 being the simplest and 1 being the most complex. Ignore all text in the image when determining this complexity. Format the response in LaTeX."

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