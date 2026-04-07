import logging
import re

from app.services.ollama_service import ollama_service
from app.core.config import settings

logger = logging.getLogger(__name__)

# Assignment rubrics: deterministic checks + AI evaluation criteria
ASSIGNMENT_RUBRICS = {
    1: {
        "name": "MySite HTML Pages",
        "max_score": 100,
        "deterministic_checks": [
            {"name": "Has aboutme page", "points": 10, "check": "aboutme"},
            {"name": "Has hobbies page", "points": 10, "check": "hobbies"},
            {"name": "Has job page", "points": 10, "check": "job"},
            {"name": "Uses navigation links", "points": 10, "check": "nav_links"},
            {"name": "Uses semantic HTML5 tags", "points": 10, "check": "semantic_tags"},
        ],
        "ai_criteria": [
            "Content quality and completeness (20 points)",
            "Proper HTML structure and nesting (15 points)",
            "Use of appropriate HTML elements (15 points)",
            "Code readability and formatting (10 points)",
        ],
    },
    2: {
        "name": "CSS Styling",
        "max_score": 100,
        "deterministic_checks": [
            {"name": "External CSS file linked", "points": 10, "check": "external_css"},
            {"name": "Uses class or id selectors", "points": 10, "check": "css_selectors"},
            {"name": "Uses box model properties", "points": 10, "check": "box_model"},
            {"name": "Consistent styling across pages", "points": 10, "check": "consistent_style"},
        ],
        "ai_criteria": [
            "Visual design quality and consistency (20 points)",
            "Appropriate use of CSS properties (20 points)",
            "Layout and spacing (10 points)",
            "Code organization (10 points)",
        ],
    },
    3: {
        "name": "Canvas Drawing",
        "max_score": 100,
        "deterministic_checks": [
            {"name": "Canvas element exists", "points": 10, "check": "canvas_element"},
            {"name": "Gets 2D context", "points": 10, "check": "get_context"},
            {"name": "Draws circle (arc)", "points": 15, "check": "draws_arc"},
            {"name": "Draws rectangle", "points": 15, "check": "draws_rect"},
            {"name": "Uses variables for position/size", "points": 10, "check": "uses_variables"},
        ],
        "ai_criteria": [
            "Correct use of Canvas API methods (20 points)",
            "Proper variable naming and usage (10 points)",
            "Code structure and comments (10 points)",
        ],
    },
    4: {
        "name": "Ball Animation",
        "max_score": 100,
        "deterministic_checks": [
            {"name": "Uses setInterval or requestAnimationFrame", "points": 15, "check": "game_loop"},
            {"name": "Uses clearRect", "points": 10, "check": "clear_rect"},
            {"name": "Has dx/dy velocity variables", "points": 15, "check": "velocity_vars"},
            {"name": "Has a draw function", "points": 10, "check": "draw_function"},
        ],
        "ai_criteria": [
            "Animation works correctly (20 points)",
            "Proper function structure (15 points)",
            "Understanding of game loop pattern (15 points)",
        ],
    },
    5: {
        "name": "Paddle & Input",
        "max_score": 100,
        "deterministic_checks": [
            {"name": "Has keydown event listener", "points": 10, "check": "keydown_listener"},
            {"name": "Has keyup event listener", "points": 10, "check": "keyup_listener"},
            {"name": "Draws paddle", "points": 10, "check": "draws_paddle"},
            {"name": "Has game over condition", "points": 10, "check": "game_over"},
        ],
        "ai_criteria": [
            "Keyboard controls work correctly (15 points)",
            "Mouse controls implemented (10 points)",
            "Paddle stays within bounds (10 points)",
            "Game over logic is correct (10 points)",
            "Code quality (15 points)",
        ],
    },
    6: {
        "name": "Brick Field",
        "max_score": 100,
        "deterministic_checks": [
            {"name": "Uses 2D array for bricks", "points": 10, "check": "2d_array"},
            {"name": "Uses nested for loops", "points": 10, "check": "nested_loops"},
            {"name": "Bricks have status property", "points": 10, "check": "brick_status"},
            {"name": "Ball-brick collision detection", "points": 15, "check": "brick_collision"},
        ],
        "ai_criteria": [
            "Brick grid renders correctly (15 points)",
            "Collision detection works properly (15 points)",
            "Bricks disappear on hit (10 points)",
            "Code organization (15 points)",
        ],
    },
    7: {
        "name": "Complete Game",
        "max_score": 100,
        "deterministic_checks": [
            {"name": "Has score display", "points": 10, "check": "score_display"},
            {"name": "Has lives display", "points": 10, "check": "lives_display"},
            {"name": "Has win condition", "points": 10, "check": "win_condition"},
            {"name": "Uses fillText for HUD", "points": 5, "check": "fill_text"},
        ],
        "ai_criteria": [
            "Game is fully playable (20 points)",
            "Score and lives work correctly (15 points)",
            "Win/lose conditions are proper (15 points)",
            "Overall code quality and structure (15 points)",
        ],
    },
    8: {
        "name": "Ball Class (OOP)",
        "max_score": 100,
        "deterministic_checks": [
            {"name": "Defines Ball class", "points": 15, "check": "ball_class"},
            {"name": "Has constructor", "points": 10, "check": "constructor"},
            {"name": "Has draw method", "points": 10, "check": "draw_method"},
            {"name": "Has move method", "points": 10, "check": "move_method"},
            {"name": "Uses this keyword", "points": 10, "check": "this_keyword"},
        ],
        "ai_criteria": [
            "Class is properly structured (15 points)",
            "Methods encapsulate behavior correctly (15 points)",
            "Game still works with the class (15 points)",
        ],
    },
    9: {
        "name": "Full OOP Refactor",
        "max_score": 100,
        "deterministic_checks": [
            {"name": "Has Ball class", "points": 8, "check": "ball_class"},
            {"name": "Has Paddle class", "points": 8, "check": "paddle_class"},
            {"name": "Has Brick class", "points": 8, "check": "brick_class"},
            {"name": "Has Game class", "points": 8, "check": "game_class"},
            {"name": "Uses external JS files", "points": 8, "check": "external_scripts"},
        ],
        "ai_criteria": [
            "All classes properly structured (15 points)",
            "Single responsibility principle followed (15 points)",
            "Game class orchestrates correctly (15 points)",
            "Code modularity and organization (15 points)",
        ],
    },
}


def run_deterministic_checks(assignment_id: int, code: str, files: dict = None) -> list:
    """Run automated checks against submitted code. Returns list of {name, points, passed}."""
    rubric = ASSIGNMENT_RUBRICS.get(assignment_id)
    if not rubric:
        return []

    # Combine all code sources
    all_code = code or ""
    if files:
        for content in files.values():
            all_code += "\n" + content

    all_code_lower = all_code.lower()
    results = []

    for check in rubric["deterministic_checks"]:
        passed = _run_check(check["check"], all_code, all_code_lower, files)
        results.append({
            "name": check["name"],
            "points": check["points"] if passed else 0,
            "max_points": check["points"],
            "passed": passed,
        })

    return results


def _run_check(check_type: str, code: str, code_lower: str, files: dict = None) -> bool:
    """Run a single deterministic check."""
    checks = {
        "aboutme": lambda: _has_file_or_content(files, code_lower, ["aboutme", "about_me", "about-me"]),
        "hobbies": lambda: _has_file_or_content(files, code_lower, ["hobbies", "hobby"]),
        "job": lambda: _has_file_or_content(files, code_lower, ["job", "career", "work"]),
        "nav_links": lambda: "<nav" in code_lower or ('href=' in code_lower and code_lower.count('href=') >= 3),
        "semantic_tags": lambda: any(tag in code_lower for tag in ["<header", "<footer", "<section", "<article", "<nav"]),
        "external_css": lambda: 'rel="stylesheet"' in code_lower or "rel='stylesheet'" in code_lower,
        "css_selectors": lambda: bool(re.search(r'\.\w+\s*\{', code) or re.search(r'#\w+\s*\{', code)),
        "box_model": lambda: any(p in code_lower for p in ["margin", "padding", "border"]),
        "consistent_style": lambda: "link" in code_lower and "stylesheet" in code_lower,
        "canvas_element": lambda: "<canvas" in code_lower,
        "get_context": lambda: "getcontext" in code_lower,
        "draws_arc": lambda: ".arc(" in code_lower,
        "draws_rect": lambda: ".rect(" in code_lower or ".fillrect(" in code_lower,
        "uses_variables": lambda: bool(re.search(r'\b(let|const|var)\s+\w+\s*=\s*\d+', code)),
        "game_loop": lambda: "setinterval" in code_lower or "requestanimationframe" in code_lower,
        "clear_rect": lambda: "clearrect" in code_lower,
        "velocity_vars": lambda: bool(re.search(r'\b(dx|dy)\b', code)),
        "draw_function": lambda: bool(re.search(r'function\s+draw', code_lower) or re.search(r'draw\s*\(', code)),
        "keydown_listener": lambda: "keydown" in code_lower,
        "keyup_listener": lambda: "keyup" in code_lower,
        "draws_paddle": lambda: "paddle" in code_lower,
        "game_over": lambda: "game over" in code_lower or "gameover" in code_lower or "location.reload" in code_lower,
        "2d_array": lambda: bool(re.search(r'\[.*\[', code)),
        "nested_loops": lambda: code_lower.count("for") >= 2 or code_lower.count("for(") >= 2,
        "brick_status": lambda: "status" in code_lower,
        "brick_collision": lambda: "collision" in code_lower or (code_lower.count("if") >= 3 and "brick" in code_lower),
        "score_display": lambda: "score" in code_lower,
        "lives_display": lambda: "lives" in code_lower or "life" in code_lower,
        "win_condition": lambda: ("win" in code_lower or "you win" in code_lower or "congratulations" in code_lower),
        "fill_text": lambda: "filltext" in code_lower,
        "ball_class": lambda: bool(re.search(r'class\s+Ball', code)),
        "constructor": lambda: "constructor(" in code,
        "draw_method": lambda: bool(re.search(r'draw\s*\(', code)),
        "move_method": lambda: bool(re.search(r'move\s*\(', code)),
        "this_keyword": lambda: "this." in code,
        "paddle_class": lambda: bool(re.search(r'class\s+Paddle', code)),
        "brick_class": lambda: bool(re.search(r'class\s+Brick', code)),
        "game_class": lambda: bool(re.search(r'class\s+Game', code)),
        "external_scripts": lambda: code_lower.count('src=') >= 3 or (files and len(files) >= 3),
    }

    check_fn = checks.get(check_type)
    if check_fn:
        try:
            return check_fn()
        except Exception:
            return False
    return False


def _has_file_or_content(files: dict, code_lower: str, keywords: list) -> bool:
    """Check if any keyword appears in filenames or code content."""
    if files:
        for filename in files:
            if any(kw in filename.lower() for kw in keywords):
                return True
    return any(kw in code_lower for kw in keywords)


async def ai_evaluate(assignment_id: int, code: str, files: dict = None, deterministic_results: list = None, language: str = "en") -> dict:
    """Use AI to evaluate code quality against rubric criteria."""
    rubric = ASSIGNMENT_RUBRICS.get(assignment_id)
    if not rubric:
        return {"ai_score": 0, "ai_feedback": "Unknown assignment", "ai_max": 0}

    # Calculate remaining points after deterministic checks
    det_max = sum(c["max_points"] for c in (deterministic_results or []))
    ai_max = rubric["max_score"] - sum(c["points"] for c in rubric["deterministic_checks"])

    all_code = code or ""
    if files:
        for fname, content in files.items():
            all_code += f"\n\n// === {fname} ===\n{content}"

    # Truncate very long submissions
    if len(all_code) > 15000:
        all_code = all_code[:15000] + "\n... (truncated)"

    language_names = {"en": "English", "ja": "Japanese", "zh": "Chinese", "ko": "Korean", "es": "Spanish"}
    feedback_lang = language_names.get(language, "English")

    prompt = f"""You are grading a student's Assignment {assignment_id}: {rubric['name']} for a Web Programming course.
The students are beginners with no prior programming experience.

AI Evaluation Criteria (total {ai_max} points):
{chr(10).join(f'- {c}' for c in rubric['ai_criteria'])}

Deterministic check results:
{chr(10).join(f"- {r['name']}: {'PASS' if r['passed'] else 'FAIL'} ({r['points']}/{r['max_points']} pts)" for r in (deterministic_results or []))}

Student's submitted code:
```
{all_code}
```

Provide your evaluation in exactly this format:
AI_SCORE: [number out of {ai_max}]
FEEDBACK: [2-4 sentences of constructive feedback in {feedback_lang}]
BREAKDOWN:
{chr(10).join(f'- {c}: [score]' for c in rubric['ai_criteria'])}
"""

    try:
        response = await ollama_service.generate(prompt, temperature=0.3, max_tokens=1000)

        # Parse AI score
        ai_score = 0
        score_match = re.search(r'AI_SCORE:\s*(\d+)', response)
        if score_match:
            ai_score = min(int(score_match.group(1)), ai_max)

        # Parse feedback
        feedback_match = re.search(r'FEEDBACK:\s*(.+?)(?=BREAKDOWN:|$)', response, re.DOTALL)
        ai_feedback = feedback_match.group(1).strip() if feedback_match else response

        return {
            "ai_score": ai_score,
            "ai_max": ai_max,
            "ai_feedback": ai_feedback,
            "ai_raw_response": response,
        }
    except Exception as e:
        logger.error(f"AI evaluation error: {e}")
        return {
            "ai_score": 0,
            "ai_max": ai_max,
            "ai_feedback": f"AI evaluation failed: {str(e)}",
            "ai_raw_response": "",
        }


def get_rubric(assignment_id: int) -> dict:
    return ASSIGNMENT_RUBRICS.get(assignment_id)
