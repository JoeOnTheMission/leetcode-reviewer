# main.py

import sys
import time
from scraper.submissions import extract_submissions
from ai.reviewer import full_review, light_review
from notes.generator import generate_note
from neetcode import has_neetcode_video


def process_problem(problem_url: str):
    """Run the full pipeline for a single problem URL."""
    print("\n" + "=" * 40)
    print(f"  Processing: {problem_url}")
    print("=" * 40)

    result = extract_submissions(problem_url)

    print(f"\n  Problem     : {result['problem_title']}")
    print(f"  Submissions : {result['total_submissions']} total, {result['accepted_submissions']} accepted")

    # Extract slug for NeetCode check
    slug = problem_url.strip("/").split("/")
    slug = slug[slug.index("problems") + 1]
    neetcode = has_neetcode_video(slug)
    print(f"  NeetCode    : {'Yes' if neetcode else 'No video'}")

    print("\n[AI] Running full review on latest submission...")
    latest_review = full_review(
        result['latest']['code'],
        result['latest']['lang'],
        result['problem_title'],
    )
    older_reviews = []
    for i, sub in enumerate(result['older'], 1):
        print(f"[AI] Running light review on older submission {i}...")
        review = light_review(sub['code'], sub['lang'], sub['status'])
        older_reviews.append(review)

    print("\n[NOTE] Generating Obsidian note...")
    filepath = generate_note(
        problem_title=result['problem_title'],
        problem_url=problem_url,
        problem_tags=result['problem_tags'],
        latest_date=result['latest_date'],
        latest=result['latest'],
        latest_review=latest_review,
        older=result['older'],
        older_reviews=older_reviews,
        total_submissions=result['total_submissions'],
        accepted_submissions=result['accepted_submissions'],
        has_neetcode=neetcode,
    )

    print(f"  ✅ Saved: {filepath}")
    return filepath


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Single problem : python main.py <url>")
        print("  Multiple       : python main.py <url1> <url2> <url3>")
        print("  From file      : python main.py --file urls.txt")
        sys.exit(1)

    # Collect URLs
    if sys.argv[1] == "--file":
        if len(sys.argv) < 3:
            print("Error: provide a file path after --file")
            sys.exit(1)
        with open(sys.argv[2], "r") as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    else:
        urls = sys.argv[1:]

    print(f"\n{'=' * 40}")
    print(f"   LeetCode Review Automator")
    print(f"   Processing {len(urls)} problem(s)")
    print(f"{'=' * 40}")

    results = []
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Starting...")
        try:
            filepath = process_problem(url)
            results.append((url, True, filepath))
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            results.append((url, False, str(e)))

        # Avoid rate limiting when processing multiple problems
        if i < len(urls):
            print("\n  Waiting 3 seconds before next problem...")
            time.sleep(3)

    # Final summary
    print(f"\n{'=' * 40}")
    print(f"  SUMMARY ({len(urls)} problems)")
    print(f"{'=' * 40}")
    for url, success, info in results:
        slug = url.strip("/").split("/problems/")[-1].split("/")[0]
        status = "✅" if success else "❌"
        print(f"  {status} {slug}")


if __name__ == "__main__":
    main()