"""Accessibility checks (subset of soul-forge-gate rules)."""
import re
from dataclasses import dataclass
from typing import List


@dataclass
class CheckResult:
    rule: str
    passed: bool
    message: str


def check_html_lang(html: str) -> CheckResult:
    m = re.search(r"<html[^>]*\blang\s*=\s*[\"']([^\"']+)[\"']", html, re.IGNORECASE)
    if m:
        return CheckResult("html-lang", True, f"lang={m.group(1)}")
    return CheckResult("html-lang", False, "Missing lang attribute on <html>")


def check_img_alt(html: str) -> List[CheckResult]:
    results = []
    for m in re.finditer(r"<img\b[^>]*>", html, re.IGNORECASE):
        tag = m.group(0)
        if re.search(r"\balt\s*=", tag, re.IGNORECASE):
            results.append(CheckResult("img-alt", True, "alt present"))
        else:
            results.append(CheckResult("img-alt", False, f"Missing alt: {tag[:50]}"))
    if not results:
        results.append(CheckResult("img-alt", True, "No images found"))
    return results


def _parse_color(c: str):
    c = c.strip().lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    if len(c) != 6:
        return None
    try:
        return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    except ValueError:
        return None


def _relative_luminance(rgb):
    def chan(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * chan(r) + 0.7152 * chan(g) + 0.0722 * chan(b)


def contrast_ratio(fg: str, bg: str) -> float:
    fg_rgb = _parse_color(fg)
    bg_rgb = _parse_color(bg)
    if not fg_rgb or not bg_rgb:
        return 0.0
    l1 = _relative_luminance(fg_rgb)
    l2 = _relative_luminance(bg_rgb)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return round((lighter + 0.05) / (darker + 0.05), 2)


def check_contrast(html: str, min_ratio: float = 4.5) -> List[CheckResult]:
    results = []
    # Look for inline style color pairs
    for m in re.finditer(r"color:\s*(#[0-9a-fA-F]{3,6})", html):
        fg = m.group(1)
        # Try to find background-color nearby
        bg_match = re.search(r"background(?:-color)?:\s*(#[0-9a-fA-F]{3,6})", html)
        bg = bg_match.group(1) if bg_match else "#ffffff"
        ratio = contrast_ratio(fg, bg)
        passed = ratio >= min_ratio
        results.append(CheckResult(
            "contrast",
            passed,
            f"ratio={ratio} (min {min_ratio}) fg={fg} bg={bg}",
        ))
    if not results:
        results.append(CheckResult("contrast", True, "No inline colors found"))
    return results


def check_form_labels(html: str) -> List[CheckResult]:
    results = []
    for m in re.finditer(r"<input\b[^>]*>", html, re.IGNORECASE):
        tag = m.group(0)
        if re.search(r"\bid\s*=", tag, re.IGNORECASE):
            input_id = re.search(r"\bid\s*=\s*[\"']([^\"']+)[\"']", tag, re.IGNORECASE)
            if input_id:
                iid = input_id.group(1)
                if f'for="{iid}"' in html or f"for='{iid}'" in html:
                    results.append(CheckResult("form-label", True, f"label for {iid}"))
                else:
                    results.append(CheckResult("form-label", False, f"No label for input id={iid}"))
            else:
                results.append(CheckResult("form-label", True, "No id"))
        else:
            # input without id — check for aria-label
            if "aria-label" in tag.lower():
                results.append(CheckResult("form-label", True, "aria-label present"))
            else:
                results.append(CheckResult("form-label", False, f"Input without id or aria-label: {tag[:50]}"))
    if not results:
        results.append(CheckResult("form-label", True, "No inputs found"))
    return results


def run_all(html: str) -> List[CheckResult]:
    results = [check_html_lang(html)]
    results.extend(check_img_alt(html))
    results.extend(check_contrast(html))
    results.extend(check_form_labels(html))
    return results
