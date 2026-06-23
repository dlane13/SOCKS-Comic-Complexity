import ollama
from pathlib import Path

IMAGES_PATH = Path('/Users/darbylane/Library/CloudStorage/OneDrive-UniversityofVermont/'
                   'VEA study - tasks for students/SOCKS project/CH Corpus/Originals')

response = ollama.chat(
    model="qwen2.5vl:7b",
    messages=[{
        "role": "user",
        "content": "Consider the following: “Macros” (panels depicting an entire scene) are more explicit in terms of semantic content, and should thus be easier to understand and less complex (0 on 0-1 scale), compared to “monos” (panels depicting only one character or object) or “micros” (which show a “zoomed in” part of a character, object, or scene), which provide less information and are thus more complex (1 on 0-1 scale). Given this information, describe the complexity of the framing structure of the comic, and rate the framing complexity on a scale of 0-1, with 0 being the simplest (macros) and 1 being the most complex (monos, micros).",
        "images": [IMAGES_PATH / 'CH.1985.11.27.png']
    }]
)
print(response.message.content)

response = ollama.chat(
    model="qwen2.5vl:7b",
    messages=[{
        "role": "user",
        "content": "Consider the following: “Macros” (panels depicting an entire scene) are more explicit in terms of semantic content, and should thus be easier to understand and less complex (0 on 0-1 scale), compared to “monos” (panels depicting only one character or object) or “micros” (which show a “zoomed in” part of a character, object, or scene), which provide less information and are thus more complex (1 on 0-1 scale). Given this information, describe the complexity of the framing structure of the comic, and rate the framing complexity on a scale of 0-1, with 0 being the simplest (macros) and 1 being the most complex (monos, micros).",
        "images": [IMAGES_PATH / 'CH.1985.11.29.png']
    }]
)
print(response.message.content)