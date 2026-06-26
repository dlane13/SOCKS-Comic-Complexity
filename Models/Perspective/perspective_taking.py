import ollama
from pathlib import Path

IMAGES_PATH = Path('/Users/darbylane/Library/CloudStorage/OneDrive-UniversityofVermont/'
                   'VEA study - tasks for students/SOCKS project/CH Corpus/Originals')

PROMPT = "Consider the following:  Many comics show or imply a character’s perspective; panels without first person perspectives are simpler than those that show an implicit perspective, which are easier than those with an explicit first-person perspective. Given this information and ignoring the text in the image, describe the complexity of the perspective of the comic and your reasoning, and rate it overall on a scale of 0-1, with 0 being the simplest and 1 being the most complex. Format the response in LaTeX without any new commands."

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