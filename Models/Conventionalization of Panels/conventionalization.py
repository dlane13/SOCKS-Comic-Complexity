import ollama
from pathlib import Path

IMAGES_PATH = Path('/Users/darbylane/Library/CloudStorage/OneDrive-UniversityofVermont/'
                   'VEA study - tasks for students/SOCKS project/CH Corpus/Originals')

PROMPT = "Consider the following: Just like language, comic panels vary from using highly regularized patterns to being novel and productive representations. While regularized templates are presumably simpler than novel images as they are entrenched in readers’ memories, they also reflect knowledge in the visual language people are exposed to. Here, higher percentages of templatic panels will reflect more complexity. Given this information, describe the complexity of the comic with respect to panel conventionalization, and rate it overall on a scale of 0-1, with 0 being the simplest and 1 being the most complex. Format the response in LaTeX."

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