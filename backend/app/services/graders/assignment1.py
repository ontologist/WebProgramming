# Copyright (c) 2026 Yuri Tijerino. All rights reserved.
# 著作権 (c) 2026 ティヘリノ ユリ. 全著作権所有.
# Unauthorized copying, modification, or distribution of this file is prohibited.
# 本ファイルの無断複製、改変、配布を禁じます。
"""
Grader for Assignment 1 — MySite HTML Pages.

Rubric (from the assignment page, total 100):
  - Personal content quality & completeness    30
  - Advanced HTML/CSS techniques (min 5)       30
  - Visual design creativity & uniqueness      20
  - Code quality & structure                   10
  - Navigation & consistency                   10

Layer split:
  Deterministic (60 pts)            AI (40 pts)
    Content completeness 20           Content quality prose    10
    Techniques detected  30           Visual design            20
    Navigation           10           Code readability         10
    HTML validity         5           (sums to 40)
    (sums to 65, but content-quality 10 and code-readability 5
     live on the AI side — see DET_MAX below)

Kill-switch: if the submission is substantially identical to the
starter template (≥70% of template paragraphs present verbatim), the
whole assignment scores zero with feedback explaining why.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from app.services.ollama_service import ollama_service
from . import base

logger = logging.getLogger(__name__)

MAX_SCORE = 100
DET_MAX = 65     # 20 + 30 + 10 + 5
AI_MAX = 35      # 10 + 20 + 5
# (DET_MAX + AI_MAX == 100)

PROSE_MODEL = "llama3.2:latest"  # prose review uses llama3.2 regardless of OLLAMA_MODEL

TEMPLATE_DIR = Path(__file__).resolve().parents[3] / ".." / "docs" / "assignments" / "MySite-template"
TEMPLATE_DIR = TEMPLATE_DIR.resolve()

_TEMPLATE_FILES = base.load_template(TEMPLATE_DIR)
_TEMPLATE_PARAGRAPHS: dict[str, set[str]] = {
    name: {p for p in base.html_to_paragraphs(content) if len(p) >= 20}
    for name, content in _TEMPLATE_FILES.items()
}
# Strong template signatures that appear across all three personal pages:
# - the header placeholder name ("関学太郎")
# - Tijerino's footer copyright
_STRONG_SIGNATURES = ("関学太郎", "2022 Yuri Tijerino")

UNCHANGED_THRESHOLD = 0.70  # ≥70% of template paragraphs still present -> kill-switch
EXPECTED_PAGES = ("aboutme.htm", "hobbies.htm", "job.htm")

# ---------------------------------------------------------------------------
# Technique signatures (16 items from the assignment page). Each matches any
# of the submitted HTM/HTML/CSS files; detection is case-insensitive and
# operates on concatenated text, so inline <style> and linked CSS both count.
# ---------------------------------------------------------------------------

_TECHNIQUES: dict[str, re.Pattern] = {
    "CSS colors / gradients":   re.compile(r"linear-gradient\(|radial-gradient\(|conic-gradient\(", re.I),
    "Google Fonts":             re.compile(r"fonts\.googleapis\.com|@import\s+url\([^)]*fonts", re.I),
    "Borders / rounded corners":re.compile(r"border-radius\s*:", re.I),
    "Shadows":                  re.compile(r"box-shadow\s*:|text-shadow\s*:", re.I),
    "Transitions / animations": re.compile(r"transition\s*:|animation\s*:|@keyframes\b", re.I),
    "CSS Grid":                 re.compile(r"display\s*:\s*grid|grid-template", re.I),
    "CSS Flexbox":              re.compile(r"display\s*:\s*flex|flex-direction\s*:", re.I),
    "HTML table":               re.compile(r"<table[\s>]", re.I),
    "HTML form":                re.compile(r"<form[\s>]", re.I),
    "HTML video / audio":       re.compile(r"<video[\s>]|<audio[\s>]", re.I),
    "Hover effects":            re.compile(r":hover\b", re.I),
    "Media queries":            re.compile(r"@media\b", re.I),
    "CSS variables":            re.compile(r"--[\w-]+\s*:\s*[^;}]+|var\(\s*--", re.I),
    "Background images":        re.compile(r"background(?:-image)?\s*:[^;}]*url\(", re.I),
    "Navigation bar styling":   re.compile(r"\bnav\b[^{]{0,120}\{|\.nav[\w-]*\s*\{", re.I),
    "Image gallery":            re.compile(r"gallery|(?:<img[^>]+>\s*){3,}", re.I),
}


# ---------------------------------------------------------------------------
# Deterministic layer
# ---------------------------------------------------------------------------

def _template_unchanged(files: dict) -> tuple[bool, float, list[str]]:
    """Return (is_unchanged, overlap_ratio, reasons)."""
    overlaps: list[float] = []
    reasons: list[str] = []

    for page, template_para_set in _TEMPLATE_PARAGRAPHS.items():
        if page not in EXPECTED_PAGES:
            continue  # skip game.htm etc.
        submitted = files.get(page) if files else None
        if not submitted or not isinstance(submitted, str):
            continue
        sub_paragraphs = set(p for p in base.html_to_paragraphs(submitted) if len(p) >= 20)
        if not template_para_set:
            continue
        overlap = len(sub_paragraphs & template_para_set) / len(template_para_set)
        overlaps.append(overlap)
        if overlap >= UNCHANGED_THRESHOLD:
            reasons.append(f"{page}: {int(overlap*100)}% of the template's original paragraphs are still present")

    # Strong signatures across the whole submission: instructor name in header,
    # instructor's copyright in footer — both are dead giveaways.
    joined_text = "\n".join(
        base.all_html_text(files).splitlines()
    ) if files else ""
    for sig in _STRONG_SIGNATURES:
        if sig in joined_text:
            reasons.append(f"Template signature still present: “{sig}”")

    avg = sum(overlaps) / len(overlaps) if overlaps else 0.0
    is_unchanged = (
        (len(reasons) >= 1 and avg >= UNCHANGED_THRESHOLD)
        or len([r for r in reasons if "signature" in r]) >= 1 and avg >= UNCHANGED_THRESHOLD
    )
    # Also fire if every submitted expected page crossed threshold individually
    if not is_unchanged and overlaps and all(o >= UNCHANGED_THRESHOLD for o in overlaps):
        is_unchanged = True
    return is_unchanged, avg, reasons


def _score_content_completeness(files: dict) -> tuple[int, list[str]]:
    """Up to 20 pts: each expected page contributes 5 pts for being present
    and carrying real content (≥150 visible chars)."""
    pts = 0
    notes: list[str] = []
    for page in EXPECTED_PAGES:
        content = (files or {}).get(page)
        if not isinstance(content, str) or not content.strip():
            notes.append(f"{page}: missing")
            continue
        paragraphs = base.html_to_paragraphs(content)
        total_text = sum(len(p) for p in paragraphs)
        if total_text >= 150:
            pts += 5 + 2  # present + substantial  (5 base, 2 bonus, see note below)
        else:
            pts += 5
            notes.append(f"{page}: very short (~{total_text} chars of text)")
    # Cap at 20 (4 expected pages × 5 would be 15; substantial bonus up to 6; cap 20)
    return min(pts, 20), notes


def _detect_techniques(files: dict) -> list[str]:
    """Regex pass — returns the candidate list (may contain false positives)."""
    blob = base.all_html_text(files)
    if not blob:
        return []
    return [name for name, pattern in _TECHNIQUES.items() if pattern.search(blob)]


def _score_from_confirmed(confirmed_count: int) -> int:
    """30-pt bucket: 6 pts per confirmed technique, capped at 5."""
    return min(confirmed_count, 5) * 6


async def _verify_techniques(files: dict, candidates: list[str]) -> tuple[list[str], list[dict], str]:
    """Ask llama3.2 to confirm each regex-flagged technique is really being
    used (not commented-out, not a coincidental text match, etc.).

    Verify-only: the model cannot add techniques beyond the candidate list.
    On model failure or unparseable output, falls back to the raw candidate
    list (so a model hiccup never penalizes the student).

    Returns (confirmed_names, rejections, raw_response)
      - confirmed_names: subset of candidates the model accepted (or all
        candidates if the fallback fired).
      - rejections: list of {"name", "reason"} for each rejected candidate.
      - raw_response: the model's raw text, for the submission audit trail.
    """
    if not candidates:
        return [], [], ""

    blob_parts: list[str] = []
    for fname, content in (files or {}).items():
        if isinstance(content, str) and fname.lower().endswith((".htm", ".html", ".css")):
            blob_parts.append(f"// === {fname} ===\n{content}")
    blob = "\n\n".join(blob_parts)
    if len(blob) > 12000:
        blob = blob[:12000] + "\n... (truncated)"

    numbered = "\n".join(f"{i+1}. {name}" for i, name in enumerate(candidates))

    prompt = f"""You are auditing an automatic technique-detector for a beginner Web Programming student's submission.

A regex pass flagged the following candidate techniques as present in the student's HTML/CSS:
{numbered}

Your job: for EACH candidate in the list above, decide whether it is actually being used as a real styling or markup technique in the submitted code. A candidate should be rejected ("confirmed": false) if:
  - the match is only inside a comment
  - the match is only inside plain text content (not a CSS rule or tag)
  - the code is present but commented out or not actually rendered
  - the match is a false positive (e.g. the word "gallery" used in a paragraph, not a real image gallery)

Rules:
- Do NOT add techniques that are not in the list above.
- Return STRICTLY valid JSON with exactly this shape:
  {{"techniques": [{{"name": "<exact name from list>", "confirmed": true|false, "reason": "<one short sentence>"}}]}}
- Include every candidate from the list, in the same order.
- "reason" must be in English and under 20 words.

Student's code:
```
{blob}
```
"""

    try:
        raw = await ollama_service.generate(
            prompt,
            temperature=0.1,
            max_tokens=900,
            model=PROSE_MODEL,
        )
    except Exception as e:
        logger.error(f"assignment1 technique-verify failed, falling back to regex: {e}")
        return list(candidates), [], f"[verify_failed: {e}]"

    confirmed, rejections = _parse_verification(raw, candidates)
    if confirmed is None:
        # Unparseable response — fall back to raw regex count, no rejections.
        logger.warning("assignment1 technique-verify: could not parse model response, using raw regex list")
        return list(candidates), [], raw
    return confirmed, rejections, raw


def _parse_verification(raw: str, candidates: list[str]) -> tuple[list[str] | None, list[dict]]:
    """Returns (confirmed_list, rejections). confirmed_list is None if the
    response could not be parsed at all."""
    candidate_set = {c.lower() for c in candidates}

    for candidate_json in _extract_json_candidates(raw):
        try:
            obj = json.loads(candidate_json)
        except Exception:
            continue
        if not isinstance(obj, dict):
            continue
        items = obj.get("techniques")
        if not isinstance(items, list):
            continue

        confirmed: list[str] = []
        rejections: list[dict] = []
        seen: set[str] = set()
        # Build a lookup of candidate names so we preserve original casing.
        original_by_lower = {c.lower(): c for c in candidates}

        for entry in items:
            if not isinstance(entry, dict):
                continue
            name = str(entry.get("name", "")).strip()
            if not name or name.lower() not in candidate_set or name.lower() in seen:
                continue  # verify-only: drop anything not in the candidate list
            seen.add(name.lower())
            orig = original_by_lower[name.lower()]
            confirmed_flag = bool(entry.get("confirmed"))
            reason = str(entry.get("reason", "")).strip()
            if confirmed_flag:
                confirmed.append(orig)
            else:
                rejections.append({"name": orig, "reason": reason or "(no reason provided)"})

        # Any candidate the model forgot about → treat as confirmed (verify-only
        # fallback: we only remove on explicit rejection).
        for name in candidates:
            if name.lower() not in seen:
                confirmed.append(name)

        return confirmed, rejections

    return None, []


def _score_navigation(files: dict) -> tuple[int, list[str]]:
    """Up to 10 pts: proportional to how many of the three expected pages link
    to every one of their siblings (aboutme/hobbies/job/game)."""
    if not files:
        return 0, ["no files submitted"]
    siblings = {"aboutme.htm", "hobbies.htm", "job.htm", "game.htm"}
    passed = 0
    notes: list[str] = []
    for page in EXPECTED_PAGES:
        content = files.get(page)
        if not isinstance(content, str):
            continue
        hrefs = {h.split("#")[0].split("?")[0].lower() for h in base.extract_hrefs(content)}
        expected = siblings - {page.lower()}
        if expected.issubset(hrefs):
            passed += 1
        else:
            missing = sorted(expected - hrefs)
            notes.append(f"{page} missing links to: {', '.join(missing)}")
    pts = round(passed * 10 / len(EXPECTED_PAGES))
    return pts, notes


def _score_html_validity(files: dict) -> tuple[int, list[str]]:
    """Up to 5 pts based on tag-mismatch count across expected pages.
    0 errors -> 5, 1-3 -> 3, 4-8 -> 1, else 0."""
    total = 0
    notes: list[str] = []
    for page in EXPECTED_PAGES:
        content = (files or {}).get(page)
        if not isinstance(content, str):
            continue
        errs = base.count_tag_mismatches(content)
        total += errs
        if errs:
            notes.append(f"{page}: {errs} tag mismatch{'es' if errs != 1 else ''}")
    if total == 0:
        return 5, notes
    if total <= 3:
        return 3, notes
    if total <= 8:
        return 1, notes
    return 0, notes


async def deterministic(code: str | None, files: dict | None) -> list[dict]:
    files = files or {}

    is_unchanged, overlap, reasons = _template_unchanged(files)
    if is_unchanged:
        return [{
            "name": "Template submitted unchanged — zero score",
            "points": 0,
            "max_points": MAX_SCORE,
            "passed": False,
            "details": "; ".join(reasons) if reasons else f"{int(overlap*100)}% of the template still present",
            "zero_assignment": True,
        }]

    content_pts, content_notes = _score_content_completeness(files)
    nav_pts, nav_notes = _score_navigation(files)
    html_pts, html_notes = _score_html_validity(files)

    # Techniques: regex finds candidates, then llama3.2 rejects false positives.
    candidates = _detect_techniques(files)
    confirmed, rejections, verify_raw = await _verify_techniques(files, candidates)
    tech_pts = _score_from_confirmed(len(confirmed))

    if not candidates:
        tech_details = "no advanced techniques detected"
    else:
        parts = [f"detected by regex: {', '.join(candidates)}"]
        if rejections:
            parts.append("AI-rejected: " + "; ".join(f"{r['name']} ({r['reason']})" for r in rejections))
        parts.append(f"confirmed: {', '.join(confirmed)}" if confirmed else "confirmed: (none)")
        tech_details = " | ".join(parts)

    return [
        {
            "name": "Personal content completeness (pages + length)",
            "points": content_pts, "max_points": 20, "passed": content_pts >= 15,
            "details": "; ".join(content_notes) if content_notes else "all expected pages present with content",
        },
        {
            "name": f"Advanced HTML/CSS techniques ({len(confirmed)}/5 needed)",
            "points": tech_pts, "max_points": 30, "passed": tech_pts >= 30,
            "details": tech_details,
            "techniques_detected": candidates,
            "techniques_confirmed": confirmed,
            "techniques_rejected": rejections,
            "techniques_verify_raw": verify_raw,
        },
        {
            "name": "Navigation to all sibling pages",
            "points": nav_pts, "max_points": 10, "passed": nav_pts >= 10,
            "details": "; ".join(nav_notes) if nav_notes else "every page links to every sibling",
        },
        {
            "name": "HTML validity",
            "points": html_pts, "max_points": 5, "passed": html_pts >= 5,
            "details": "; ".join(html_notes) if html_notes else "no tag mismatches",
        },
    ]


# ---------------------------------------------------------------------------
# AI layer (prose)
# ---------------------------------------------------------------------------

_LANG_NAMES = {"en": "English", "ja": "Japanese", "zh": "Chinese", "ko": "Korean", "es": "Spanish"}


def _should_zero_assignment(det_results: list[dict] | None) -> bool:
    if not det_results:
        return False
    return any(r.get("zero_assignment") for r in det_results)


async def ai_evaluate(code: str | None, files: dict | None,
                      det_results: list[dict] | None, language: str = "en") -> dict:
    # Respect the deterministic kill-switch.
    if _should_zero_assignment(det_results):
        msg = {
            "en": "This looks like the unmodified MySite template. Please replace ALL placeholder content (text, headings, and the template author's name/copyright) with your own information, apply at least 5 advanced HTML/CSS techniques, and resubmit.",
            "ja": "提出物はMySiteテンプレートが未変更のままです。すべてのプレースホルダー（本文、見出し、テンプレート作者の名前と著作権表示）を自分の情報に置き換え、少なくとも5つの高度なHTML/CSSテクニックを適用して再提出してください。",
            "zh": "此提交看起来是未修改的MySite模板。请用您自己的信息替换所有占位符内容（文本、标题和模板作者的姓名/版权），应用至少5种高级HTML/CSS技术，然后重新提交。",
            "ko": "제출물이 수정되지 않은 MySite 템플릿입니다. 모든 플레이스홀더(본문, 제목, 템플릿 작성자의 이름/저작권)를 본인의 정보로 교체하고 최소 5가지 고급 HTML/CSS 기법을 적용한 뒤 다시 제출해 주세요.",
            "es": "Esta entrega parece la plantilla MySite sin modificar. Reemplace TODO el contenido de marcador de posición (texto, encabezados y el nombre/copyright del autor de la plantilla) con su propia información, aplique al menos 5 técnicas avanzadas de HTML/CSS y vuelva a enviar.",
        }.get(language, None)
        msg = msg or msg or ""
        return {
            "ai_score": 0,
            "ai_max": AI_MAX,
            "ai_feedback": msg or "Template submitted unchanged — please replace placeholders and resubmit.",
            "ai_raw_response": "[zeroed: template_unchanged]",
        }

    det_summary = "\n".join(
        f"- {r['name']}: {r['points']}/{r['max_points']}"
        + (f"  ({r['details']})" if r.get("details") else "")
        for r in (det_results or [])
    )

    blob_parts: list[str] = []
    if code:
        blob_parts.append(f"// === pasted code ===\n{code}")
    for name, content in (files or {}).items():
        if not isinstance(content, str):
            continue
        blob_parts.append(f"// === {name} ===\n{content}")
    blob = "\n\n".join(blob_parts)
    if len(blob) > 15000:
        blob = blob[:15000] + "\n... (truncated)"

    feedback_lang = _LANG_NAMES.get(language, "English")

    prompt = f"""You are grading Assignment 1 (MySite HTML Pages) for a beginner Web Programming course.

A deterministic layer has already scored the objective checks:
{det_summary}

The remaining {AI_MAX} points are yours to award on the subjective criteria.
Score each independently, then sum:
  - content_quality_score (0-10): Is the writing personal, specific, and in the student's own voice? Does it feel like a real introduction and not filler?
  - design_creativity_score (0-20): Does the CSS make the site feel uniquely theirs? Are colour, layout, typography, and imagery used with intent?
  - code_readability_score (0-5): Are files indented consistently, with sensible naming and light comments where useful?

Write feedback in {feedback_lang}, 2-4 sentences, constructive and specific (cite filenames or choices you saw).

Return STRICTLY valid JSON with exactly these keys:
{{"content_quality_score": <int 0-10>, "design_creativity_score": <int 0-20>, "code_readability_score": <int 0-5>, "feedback": "<string>"}}

Student's submission:
```
{blob}
```
"""

    try:
        raw = await ollama_service.generate(
            prompt,
            temperature=0.3,
            max_tokens=700,
            model=PROSE_MODEL,
        )
    except Exception as e:
        logger.error(f"assignment1 AI evaluation failed: {e}")
        return {
            "ai_score": 0,
            "ai_max": AI_MAX,
            "ai_feedback": f"AI evaluation failed: {e}",
            "ai_raw_response": "",
        }

    content_q, design_c, code_r, feedback = _parse_ai_response(raw)
    ai_score = max(0, min(content_q, 10)) + max(0, min(design_c, 20)) + max(0, min(code_r, 5))
    ai_score = min(ai_score, AI_MAX)

    return {
        "ai_score": ai_score,
        "ai_max": AI_MAX,
        "ai_feedback": feedback or "(AI returned no feedback)",
        "ai_raw_response": raw,
    }


def _parse_ai_response(raw: str) -> tuple[int, int, int, str]:
    """Best-effort parse of the model's JSON reply."""
    # Try a direct JSON first
    for candidate in _extract_json_candidates(raw):
        try:
            obj = json.loads(candidate)
        except Exception:
            continue
        if isinstance(obj, dict):
            cq = int(obj.get("content_quality_score", 0) or 0)
            dc = int(obj.get("design_creativity_score", 0) or 0)
            cr = int(obj.get("code_readability_score", 0) or 0)
            fb = str(obj.get("feedback", "")).strip()
            return cq, dc, cr, fb
    # Fallback: regex out the numbers and keep the prose as feedback
    def _num(key, default=0):
        m = re.search(rf'"{key}"\s*:\s*(\d+)', raw)
        return int(m.group(1)) if m else default
    return _num("content_quality_score"), _num("design_creativity_score"), _num("code_readability_score"), raw.strip()


def _extract_json_candidates(text: str):
    """Yield JSON-ish substrings in descending preference order."""
    # Biggest matching {...} first
    stack = []
    start = None
    candidates = []
    for i, c in enumerate(text):
        if c == "{":
            if not stack:
                start = i
            stack.append(c)
        elif c == "}" and stack:
            stack.pop()
            if not stack and start is not None:
                candidates.append(text[start:i + 1])
                start = None
    # Largest first — the model often wraps JSON in prose
    for c in sorted(candidates, key=len, reverse=True):
        yield c
