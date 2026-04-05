# notes/generator.py

import os
from config import OBSIDIAN_VAULT_PATH


def generate_note(
    problem_title, problem_url, problem_tags, latest_date,
    latest, latest_review, older, older_reviews,
    total_submissions, accepted_submissions,
    has_neetcode,          # ← add this
) -> str:
    content = _build_markdown(
        problem_title, problem_url, problem_tags, latest_date,
        latest, latest_review, older, older_reviews,
        total_submissions, accepted_submissions,
        has_neetcode,      # ← add this
    )
    return _save_to_vault(problem_title, content)


def _build_markdown(
    problem_title, problem_url, problem_tags, latest_date,
    latest, review, older, older_reviews,
    total_submissions, accepted_submissions,
    has_neetcode,          # ← add this
) -> str:
    neetcode_value = "" if has_neetcode else "No video"

    tags_str = ", ".join(tag.replace(" ", "_") for tag in problem_tags)
    lines = []

    # ── Frontmatter ──────────────────────────────────────────
    lines += [
        "---",
        f"Date: {latest_date}",
        f"Time Taken (min):",
        f"Submissions: {total_submissions}",
        f"Accepted: {accepted_submissions}",
        f"tags: [{tags_str}]",
        f"Done: false",
        "---",
    ]

    # ── Callout reminder ─────────────────────────────────────
    lines += [
        "> [!note]",
        "> - Understand – Read problem & examples twice, note constraints.",
        "> - Plan ",
        "> \t- Solve a tiny example by hand, ",
        "> \t- pick brute force → optimize.",
        "> \t- Pseudocode",
        "> - Edge Cases – List tricky inputs that could break your plan.",
        "> - Code – Write clean, clear code from your plan.",
        "> - Test – Run on examples + your own edge cases.",
        "> - Review – If wrong, debug, fix, and note what you learned.",
        "",
    ]

    # ── Question link & Notes ────────────────────────────────
    lines += [
        f"[Question Link]({problem_url})",
        "# Notes",
        "- ",
        "",
    ]

    # ── Latest Submission ────────────────────────────────────
    lines += [
        "# Latest Submission",
        "```python",
        latest["code"],
        "```",
        "### Time Complexity",
        f"- {review['time']}",
        "### Space Complexity",
        f"- {review['space']}",
        "## Optimization Review",
        f"- {review['optimization']}",
        "## Best Possible Solution",
        f"- {review['best_solution_text']}",
        "```python",
        review["best_solution_code"],
        "```",
        "## Learning Takeaways",
        f"- {review['takeaways']}",
        "",
        "## NeetCode",
        neetcode_value,
        "",
    ]

    # ── Older Submissions ────────────────────────────────────
    lines.append("# Older Submissions")

    older_numbered = list(enumerate(zip(older, older_reviews), 1))
    older_numbered.reverse()

    for attempt_num, (sub, review_text) in older_numbered:
        lines += [
            f"## Attempt {attempt_num} ({sub['status']})",
            "```python",
            sub["code"],
            "```",
            "### Quick Review",
            f"- {review_text}",
        ]

    return "\n".join(lines)


def _save_to_vault(problem_title: str, content: str) -> str:
    os.makedirs(OBSIDIAN_VAULT_PATH, exist_ok=True)
    safe_title = problem_title.replace("/", "-").replace("\\", "-")
    filepath = os.path.join(OBSIDIAN_VAULT_PATH, f"{safe_title}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath