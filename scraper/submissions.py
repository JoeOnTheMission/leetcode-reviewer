# scraper/submissions.py

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GRAPHQL_URL = "https://leetcode.com/graphql"


def _get_headers() -> dict:
    """Build request headers using session cookies from .env"""
    session = os.getenv("LEETCODE_SESSION")
    csrf = os.getenv("LEETCODE_CSRF")

    if not session or not csrf:
        raise RuntimeError(
            "Missing LEETCODE_SESSION or LEETCODE_CSRF in your .env file.\n"
            "Get them from your browser's DevTools → Application → Cookies."
        )

    return {
        "Content-Type": "application/json",
        "Cookie": f"LEETCODE_SESSION={session}; csrftoken={csrf}",
        "x-csrftoken": csrf,
        "Referer": "https://leetcode.com",
    }


def _slug_from_url(url: str) -> str:
    """
    Extract the problem slug from a LeetCode URL.
    e.g. https://leetcode.com/problems/two-sum/description/ → two-sum
    """
    parts = [p for p in url.strip("/").split("/") if p]
    try:
        idx = parts.index("problems")
        return parts[idx + 1]
    except (ValueError, IndexError):
        raise ValueError(f"Could not extract problem slug from URL: {url}")


def _fetch_problem_info(slug: str) -> dict:
    """Fetch the problem title and topic tags."""
    query = """
    query questionInfo($titleSlug: String!) {
        question(titleSlug: $titleSlug) {
            title
            questionFrontendId
            topicTags {
                name
            }
        }
    }
    """
    payload = {
        "query": query,
        "variables": {"titleSlug": slug}
    }

    response = requests.post(GRAPHQL_URL, json=payload, headers=_get_headers())
    data = response.json()

    try:
        q = data["data"]["question"]
        title = f"{q['questionFrontendId']}. {q['title']}"
        tags = ["LeetCode"] + [t["name"] for t in q.get("topicTags", [])]
        return {"title": title, "tags": tags}
    except (KeyError, TypeError):
        return {"title": slug, "tags": ["LeetCode"]}


def _fetch_all_submissions(slug: str) -> dict:
    """
    Fetch up to 50 submissions for accurate stats + top 3 for code fetching.
    Returns stats and the first 3 submission IDs/metadata.
    """
    query = """
    query submissionList($offset: Int!, $limit: Int!, $lastKey: String, $questionSlug: String!) {
        submissionList(
            offset: $offset
            limit: $limit
            lastKey: $lastKey
            questionSlug: $questionSlug
        ) {
            submissions {
                id
                statusDisplay
                lang
                timestamp
            }
        }
    }
    """
    payload = {
        "query": query,
        "variables": {
            "offset": 0,
            "limit": 50,
            "lastKey": None,
            "questionSlug": slug,
        }
    }

    response = requests.post(GRAPHQL_URL, json=payload, headers=_get_headers())

    if response.status_code != 200:
        raise RuntimeError(
            f"LeetCode API returned status {response.status_code}.\n"
            f"Response: {response.text[:300]}"
        )

    data = response.json()

    try:
        submissions = data["data"]["submissionList"]["submissions"]
    except (KeyError, TypeError):
        raise RuntimeError(f"Unexpected API response: {data}")

    if not submissions:
        raise RuntimeError("No submissions found. Have you submitted this problem?")

    total = len(submissions)
    accepted = sum(1 for s in submissions if s["statusDisplay"] == "Accepted")
    latest_date = datetime.fromtimestamp(int(submissions[0]["timestamp"])).strftime("%Y-%m-%d")

    return {
        "total": total,
        "accepted": accepted,
        "latest_date": latest_date,
        "top3": submissions[:3],
    }

def _fetch_submission_code(submission_id: str) -> str:
    """
    Given a submission ID, fetch the actual code via submissionDetails.
    """
    query = """
    query submissionDetails($submissionId: Int!) {
        submissionDetails(submissionId: $submissionId) {
            code
        }
    }
    """
    payload = {
        "query": query,
        "variables": {"submissionId": int(submission_id)}
    }

    response = requests.post(GRAPHQL_URL, json=payload, headers=_get_headers())

    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to fetch code for submission {submission_id}. "
            f"Status: {response.status_code}"
        )

    data = response.json()

    try:
        return data["data"]["submissionDetails"]["code"]
    except (KeyError, TypeError):
        raise RuntimeError(
            f"Could not extract code for submission {submission_id}. "
            f"Response: {data}"
        )
def extract_submissions(problem_url: str) -> dict:
    print("\n[1/3] Parsing problem URL...")
    slug = _slug_from_url(problem_url)
    print(f"       Slug: {slug}")

    print("\n[2/3] Fetching problem info...")
    info = _fetch_problem_info(slug)
    print(f"       Title: {info['title']}")
    print(f"       Tags : {info['tags']}")

    print("\n[3/3] Fetching submissions...")
    all_data = _fetch_all_submissions(slug)
    print(f"       Total: {all_data['total']} | Accepted: {all_data['accepted']} | Date: {all_data['latest_date']}")

    results = []
    for i, sub in enumerate(all_data["top3"]):
        print(f"       Fetching code {i + 1}/{len(all_data['top3'])}...")
        code = _fetch_submission_code(sub["id"])
        results.append({
            "code": code,
            "lang": sub["lang"],
            "status": sub["statusDisplay"],
        })

    return {
        "problem_title": info["title"],
        "problem_tags": info["tags"],
        "latest_date": all_data["latest_date"],
        "total_submissions": all_data["total"],
        "accepted_submissions": all_data["accepted"],
        "latest": results[0],
        "older": results[1:],
    }