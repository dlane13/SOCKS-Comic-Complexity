import csv
import json
import os
import re
from io import BytesIO
from pathlib import Path
from typing import Optional, Union

import fire
from termcolor import cprint

from models.datatypes import RawMediaItem, RawMessage, RawTextItem
from models.llama4.generation import Llama4

THIS_DIR = Path(__file__).parent

PANEL_SCORE_PATTERN = re.compile(
    r"PANEL\s+(\d+)\s*:\s*([\d.]+)",
    re.IGNORECASE,
)


def resolve_path(path: str) -> str:
    return os.path.expanduser(path.strip("'\""))


def as_list(value: Optional[Union[str, list]]) -> list:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return value


def extract_pdf_text(path: str) -> str:
    """
    Extract all text from a PDF, preserving page boundaries.
    """
    import fitz  # PyMuPDF

    resolved = resolve_path(path)
    doc = fitz.open(resolved)

    pages = []

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text").strip()

        if text:
            pages.append(
                f"\n--- Annotation Guide: Page {page_num} ---\n{text}"
            )

    doc.close()

    return "\n".join(pages)


def load_image_media_items(image_paths: list) -> list:
    items = []

    for img_path in image_paths:
        resolved_img = resolve_path(img_path)

        with open(resolved_img, "rb") as img_f:
            items.append(
                RawMediaItem(data=BytesIO(img_f.read()))
            )

    return items


def parse_panel_scores(response_text: str) -> dict:
    """Extract {panel_number: score} from a model response."""
    scores = {}

    for match in PANEL_SCORE_PATTERN.finditer(response_text):
        panel_num = int(match.group(1))

        try:
            score = float(match.group(2))
        except ValueError:
            continue

        scores[panel_num] = score

    return scores


def run_main(
    checkpoint_dir: str,
    prompts_file: str,
    world_size: int = 1,
    max_seq_len: Optional[int] = 16384,
    max_batch_size: Optional[int] = 1,
    temperature: float = 0.6,
    top_p: float = 0.9,
    quantization_mode: Optional[str] = None,
):
    generator = Llama4.build(
        checkpoint_dir,
        max_seq_len=max_seq_len,
        max_batch_size=max_batch_size,
        world_size=world_size,
        quantization_mode=quantization_mode,
    )

    with open(prompts_file, "r") as f:
        config = json.load(f)

    entries = config["entries"]
    annotation_guide_path = config.get("annotation_guide")
    output_csv_path = resolve_path(
        config.get("output_csv", "complexity_scores.csv")
    )

    # Extract the annotation guide as TEXT once.
    guide_text = ""

    if annotation_guide_path:
        guide_text = extract_pdf_text(annotation_guide_path)

        print(
            f"Extracted annotation guide text from: "
            f"{annotation_guide_path}"
        )

        print(
            f"Annotation guide contains approximately "
            f"{len(guide_text.split())} whitespace-separated words."
        )

    # panel_scores[panel_number][feature_name] = score
    panel_scores: dict[int, dict[str, float]] = {}
    feature_order: list[str] = []

    for i, entry in enumerate(entries):
        feature_name = entry["feature_name"]
        feature_order.append(feature_name)

        prompt = entry["text"]
        image_paths = as_list(entry.get("image"))

        # Comic/panel images remain multimodal inputs.
        comic_media_items = load_image_media_items(image_paths)

        content = []

        # Annotation guide is now TEXT instead of 175 images.
        if guide_text:
            content.append(
                RawTextItem(
                    text=(
                        "ANNOTATION GUIDE\n"
                        "The following is the text extracted from "
                        "the annotation guide. Use it as the authoritative "
                        "reference for answering the question.\n\n"
                        + guide_text
                    )
                )
            )

        # Comic images remain images.
        content.extend(comic_media_items)

        # Question comes last.
        content.append(RawTextItem(text=prompt))

        user_message = RawMessage(
            role="user",
            content=content,
        )

        dialog = [user_message]

        print(
            f"\n=== Prompt {i+1}/{len(entries)}: "
            f"{feature_name} ==="
        )

        print(
            f"User: [{len(comic_media_items)} comic image(s), "
            f"annotation guide as text] "
            f"{prompt[:200]}...\n"
        )

        batch = [dialog]
        response_text = ""

        for token_results in generator.chat_completion(
            batch,
            temperature=temperature,
            top_p=top_p,
            max_gen_len=max_seq_len,
        ):
            result = token_results[0]

            if result.finished:
                break

            cprint(
                result.text,
                color="yellow",
                end="",
            )

            response_text += result.text

        print("\n")

        scores = parse_panel_scores(response_text)

        if not scores:
            print(
                f"WARNING: no PANEL <n>: <score> lines found "
                f"for feature '{feature_name}'"
            )

        for panel_num, score in scores.items():
            panel_scores.setdefault(
                panel_num, {}
            )[feature_name] = score

    # Write the CSV: one row per panel, one column per feature.
    with open(output_csv_path, "w", newline="") as csv_f:
        writer = csv.writer(csv_f)

        writer.writerow(
            ["panel"] + feature_order
        )

        for panel_num in sorted(panel_scores.keys()):
            row = [
                panel_num
            ] + [
                panel_scores[panel_num].get(
                    feature,
                    "",
                )
                for feature in feature_order
            ]

            writer.writerow(row)

    print(
        f"\nWrote scores to: {output_csv_path}"
    )


def main():
    fire.Fire(run_main)


if __name__ == "__main__":
    main()
