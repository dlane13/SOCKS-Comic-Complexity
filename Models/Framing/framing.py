import ollama
from pathlib import Path

IMAGES_PATH = Path('/Users/darbylane/Library/CloudStorage/OneDrive-UniversityofVermont/'
                   'VEA study - tasks for students/SOCKS project/CH Corpus/Originals')

PROMPT = "Consider the following definition of framing complexity: “Macros” (panels depicting an entire scene) are more explicit in terms of semantic content, and should thus be easier to understand and less complex, compared to “monos” (panels depicting only one character or object) or “micros” (which show a “zoomed in” part of a character, object, or scene), which provide less information and are thus more complex. Iterate through each panel, explaining the framing complexity in detail. Provide a summary of the complexity across all panels at the end of the response. Format the response in LaTeX."

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