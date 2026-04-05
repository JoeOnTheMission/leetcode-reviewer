import requests
import time

input_file = "Problems.txt"
output_file = "neetcode_all.py"
missing = []

def clean_text(text):
    return text.replace("聽", "").replace("\u00a0", "").strip()

def get_slug(title):
    url = "https://leetcode.com/graphql"
    
    query = {
        "query": """ 
        query($title: String!) {
          problemsetQuestionList: questionList(
            categorySlug: ""
            limit: 1
            skip: 0
            filters: { searchKeywords: $title }
          ) {
            questions: data {
              title
              titleSlug
            }
          }
        }
        """,
        "variables": {"title": title}
    }

    delay = 0.5

    for attempt in range(5):
        try:
            res = requests.post(
                url,
                json=query,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10
            )

            data = res.json()
            questions = data["data"]["problemsetQuestionList"]["questions"]

            if questions:
                return questions[0]["titleSlug"]

        except:
            pass

        time.sleep(delay)
        delay *= 2  # exponential backoff

    return None

slugs = set()

with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    title = clean_text(line)
    
    if not title:
        continue

    start = time.time()
    slug = get_slug(title)
    print(f"Time: {time.time() - start:.2f}s")

    if slug:
        slugs.add(slug)
        print(f"[{i}] ✅ {title} → {slug}")
    else:
        print(f"[{i}] ❌ Not found: {title}")
        missing.append(title)

    time.sleep(0.5)  # avoid rate limit

# Save result
with open(output_file, "w", encoding="utf-8") as f:
    f.write("NEETCODE_ALL = {\n")
    for s in sorted(slugs):
        f.write(f'    "{s}",\n')
    f.write("}\n")

print(f"\nDone! Total: {len(slugs)}")
with open("missing.txt", "w", encoding="utf-8") as f:
    for m in missing:
        f.write(m + "\n")

print(f"Missing count: {len(missing)}")