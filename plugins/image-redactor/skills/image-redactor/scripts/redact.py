#!/usr/bin/env python3
"""
Image Redactor - AWS Account IDs and specified text redaction tool.

Detects text in images using OCR and redacts sensitive information
(AWS account IDs, personal names, product names) with black rectangles.
"""

import argparse
import json
import re
from pathlib import Path

import pytesseract
from PIL import Image, ImageDraw

# Auto-detect patterns
AUTO_PATTERNS = {
    "aws_account_id": re.compile(r"\b\d{4}[-‐]?\d{4}[-‐]?\d{4}\b"),
    "aws_access_key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "aws_resource_id": re.compile(
        r"\b(?:i|vpc|sg|subnet|eni|igw|rtb|acl|nat|snap|vol|ami|lb|tgp|eip)-[0-9a-f]{8,17}\b"
    ),
    "aws_org_id": re.compile(
        r"\b(?:o-[a-z0-9]{10,32}|ou-[a-z0-9]{4}-[a-z0-9]{8,32}|r-[a-z0-9]{4})\b"
    ),
    "ip_address": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "ipv6_address": re.compile(r"\b(?:[0-9a-fA-F]{1,4}:){2,7}[0-9a-fA-F]{1,4}\b"),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "arn": re.compile(r"arn:aws[a-zA-Z-]*:[a-zA-Z0-9-]+:\S+"),
}


def detect_text_regions(image_path: str, lang: str = "jpn+eng") -> list[dict]:
    """Detect text and their bounding boxes in an image using OCR."""
    img = Image.open(image_path)
    data = pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DICT)

    regions = []
    n = len(data["text"])
    for i in range(n):
        text = data["text"][i].strip()
        if not text:
            continue
        conf = int(data["conf"][i])
        if conf < 10:
            continue
        regions.append(
            {
                "text": text,
                "x": data["left"][i],
                "y": data["top"][i],
                "w": data["width"][i],
                "h": data["height"][i],
                "conf": conf,
            }
        )
    return regions


def find_auto_redact_regions(regions: list[dict]) -> list[dict]:
    """Find regions that match auto-redact patterns (AWS account IDs, etc.)."""
    auto_redact = []

    # Check individual words
    for region in regions:
        text = region["text"]
        for pattern_name, pattern in AUTO_PATTERNS.items():
            if pattern.search(text):
                auto_redact.append({**region, "reason": pattern_name})
                break

    # Check consecutive regions for multi-word patterns (e.g., "1234 5678 9012")
    # Only match when all parts are purely numeric (with optional hyphens/parens)
    numeric_like = re.compile(r"^[\d\-‐()（）]+$")
    for i in range(len(regions) - 2):
        parts = [regions[i], regions[i + 1], regions[i + 2]]
        if not all(numeric_like.search(p["text"]) for p in parts):
            continue
        combined = "".join(p["text"] for p in parts)
        combined_clean = re.sub(r"[^0-9]", "", combined)
        if len(combined_clean) == 12 and AUTO_PATTERNS["aws_account_id"].search(combined_clean):
            for p in parts:
                if p not in auto_redact:
                    auto_redact.append({**p, "reason": "aws_account_id_part"})

    return auto_redact


def _fuzzy_digit_match(text: str, keyword: str, threshold: float = 0.7) -> bool:
    """Check if a digit-heavy text fuzzy-matches a keyword.

    Handles OCR misreads like '9848Z8573979' for '084828573970'.
    """
    # Only apply fuzzy matching for digit-heavy strings
    digit_ratio = sum(c.isdigit() for c in text) / max(len(text), 1)
    if digit_ratio < 0.5 or len(keyword) < 6:
        return False
    # Strip non-alphanumeric chars for comparison
    clean_text = re.sub(r"[^a-zA-Z0-9]", "", text)
    clean_kw = re.sub(r"[^a-zA-Z0-9]", "", keyword)
    if len(clean_text) < 4 or len(clean_kw) < 4:
        return False
    # Simple character overlap ratio
    matches = sum(a == b for a, b in zip(clean_text, clean_kw))
    ratio = matches / max(len(clean_text), len(clean_kw))
    return ratio >= threshold


def find_keyword_regions(
    regions: list[dict], keywords: list[str]
) -> list[dict]:
    """Find regions that contain any of the specified keywords."""
    matched = []
    for region in regions:
        text = region["text"]
        for keyword in keywords:
            if keyword.lower() in text.lower():
                matched.append({**region, "reason": f"keyword: {keyword}"})
                break
            elif _fuzzy_digit_match(text, keyword):
                matched.append({**region, "reason": f"keyword(fuzzy): {keyword}"})
                break
    return matched


def redact_image(
    image_path: str,
    output_path: str,
    redact_regions: list[dict],
    padding: int = 3,
) -> None:
    """Apply black rectangles over specified regions in the image."""
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    for region in redact_regions:
        x, y, w, h = region["x"], region["y"], region["w"], region["h"]
        draw.rectangle(
            [x - padding, y - padding, x + w + padding, y + h + padding],
            fill="black",
        )

    img.save(output_path)


def get_output_path(input_path: str, output_dir: str | None = None) -> str:
    """Generate output file path with _redacted suffix in a dedicated folder."""
    p = Path(input_path)
    redacted_name = f"{p.stem}_redacted{p.suffix}"
    if output_dir:
        out = Path(output_dir)
    else:
        out = p.parent / "redacted"
    out.mkdir(parents=True, exist_ok=True)
    return str(out / redacted_name)


def process_image(
    image_path: str,
    keywords: list[str] | None = None,
    output_dir: str | None = None,
    lang: str = "jpn+eng",
    interactive: bool = True,
) -> dict:
    """Process a single image: detect text, identify sensitive info, redact."""
    result = {
        "input": image_path,
        "output": None,
        "detected_texts": [],
        "auto_redacted": [],
        "keyword_redacted": [],
        "user_redacted": [],
        "status": "pending",
    }

    # Step 1: Detect all text
    regions = detect_text_regions(image_path, lang=lang)
    result["detected_texts"] = [
        {"text": r["text"], "conf": r["conf"]} for r in regions
    ]

    if not regions:
        result["status"] = "no_text_found"
        return result

    # Step 2: Auto-detect sensitive patterns
    auto_redact = find_auto_redact_regions(regions)
    result["auto_redacted"] = [
        {"text": r["text"], "reason": r["reason"]} for r in auto_redact
    ]

    # Step 3: Keyword matching
    keyword_redact = []
    if keywords:
        keyword_redact = find_keyword_regions(regions, keywords)
        result["keyword_redacted"] = [
            {"text": r["text"], "reason": r["reason"]} for r in keyword_redact
        ]

    # Combine all regions to redact
    all_redact = auto_redact + keyword_redact

    # Step 4: If interactive, output detected text for user review
    if interactive:
        result["all_detected"] = [
            {"text": r["text"], "x": r["x"], "y": r["y"], "w": r["w"], "h": r["h"]}
            for r in regions
        ]
        result["proposed_redactions"] = [
            {"text": r["text"], "reason": r.get("reason", "manual")} for r in all_redact
        ]
        result["status"] = "review_needed"
        return result

    # Step 5: Apply redaction
    if all_redact:
        output_path = get_output_path(image_path, output_dir)
        redact_image(image_path, output_path, all_redact)
        result["output"] = output_path
        result["status"] = "redacted"
    else:
        result["status"] = "no_sensitive_data"

    return result


def apply_redaction(
    image_path: str,
    regions_to_redact: list[dict],
    output_dir: str | None = None,
) -> str:
    """Apply redaction with specified regions (after user confirmation)."""
    output_path = get_output_path(image_path, output_dir)
    redact_image(image_path, output_path, regions_to_redact)
    return output_path


def review_image(
    image_path: str,
    keywords: list[str] | None = None,
    lang: str = "jpn+eng",
) -> dict:
    """Scan image and return categorized results for user review.

    Returns auto-detected sensitive items separately from general text,
    making it easy for agents to present categorized results to users.
    """
    regions = detect_text_regions(image_path, lang=lang)

    if not regions:
        return {
            "input": image_path,
            "status": "no_text_found",
            "auto_detected": [],
            "keyword_detected": [],
            "other_texts": [],
        }

    auto_redact = find_auto_redact_regions(regions)
    auto_texts = {r["text"] for r in auto_redact}

    keyword_redact = []
    keyword_texts: set[str] = set()
    if keywords:
        keyword_redact = find_keyword_regions(regions, keywords)
        keyword_texts = {r["text"] for r in keyword_redact}

    other_texts = [
        {"text": r["text"], "x": r["x"], "y": r["y"], "w": r["w"], "h": r["h"], "conf": r["conf"]}
        for r in regions
        if r["text"] not in auto_texts and r["text"] not in keyword_texts
    ]

    return {
        "input": image_path,
        "status": "review_needed",
        "auto_detected": [
            {"text": r["text"], "reason": r["reason"], "x": r["x"], "y": r["y"], "w": r["w"], "h": r["h"]}
            for r in auto_redact
        ],
        "keyword_detected": [
            {"text": r["text"], "reason": r["reason"], "x": r["x"], "y": r["y"], "w": r["w"], "h": r["h"]}
            for r in keyword_redact
        ],
        "other_texts": other_texts,
    }


def main():
    parser = argparse.ArgumentParser(description="Image redaction tool")
    subparsers = parser.add_subparsers(dest="command")

    # scan: Detect text in image (raw OCR output)
    scan_parser = subparsers.add_parser("scan", help="Scan image for text (raw)")
    scan_parser.add_argument("image", help="Image file path")
    scan_parser.add_argument("--lang", default="jpn+eng", help="OCR language")

    # review: Scan and categorize (for interactive workflow)
    review_parser = subparsers.add_parser("review", help="Scan and categorize for user review")
    review_parser.add_argument("image", help="Image file path")
    review_parser.add_argument("--keywords", nargs="*", help="Keywords to detect")
    review_parser.add_argument("--lang", default="jpn+eng", help="OCR language")

    # process: Full pipeline (non-interactive)
    proc_parser = subparsers.add_parser("process", help="Process image")
    proc_parser.add_argument("image", help="Image file path")
    proc_parser.add_argument("--keywords", nargs="*", help="Keywords to redact")
    proc_parser.add_argument("--output-dir", help="Output directory")
    proc_parser.add_argument("--lang", default="jpn+eng", help="OCR language")

    # redact: Apply redaction to specific regions
    redact_parser = subparsers.add_parser("redact", help="Apply redaction to specific regions")
    redact_parser.add_argument("image", help="Image file path")
    redact_parser.add_argument("--regions", required=True, help="JSON array of regions [{x,y,w,h}, ...]")
    redact_parser.add_argument("--output-dir", help="Output directory")

    # batch: Process folder
    batch_parser = subparsers.add_parser("batch", help="Batch process folder")
    batch_parser.add_argument("folder", help="Folder path")
    batch_parser.add_argument("--keywords", nargs="*", help="Keywords to redact")
    batch_parser.add_argument("--output-dir", help="Output directory")
    batch_parser.add_argument("--lang", default="jpn+eng", help="OCR language")

    args = parser.parse_args()

    if args.command == "scan":
        regions = detect_text_regions(args.image, lang=args.lang)
        print(json.dumps(regions, ensure_ascii=False, indent=2))

    elif args.command == "review":
        result = review_image(args.image, keywords=args.keywords, lang=args.lang)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "process":
        result = process_image(
            args.image,
            keywords=args.keywords,
            output_dir=args.output_dir,
            lang=args.lang,
            interactive=False,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "redact":
        regions = json.loads(args.regions)
        output = apply_redaction(args.image, regions, output_dir=args.output_dir)
        print(json.dumps({"output": output}, ensure_ascii=False))

    elif args.command == "batch":
        folder = Path(args.folder)
        images = list(folder.glob("*.png")) + list(folder.glob("*.jpg")) + list(folder.glob("*.jpeg"))
        results = []
        for img in images:
            if "_redacted" in img.stem:
                continue
            result = process_image(
                str(img),
                keywords=args.keywords,
                output_dir=args.output_dir,
                lang=args.lang,
                interactive=False,
            )
            results.append(result)
        print(json.dumps(results, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
