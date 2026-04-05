# 🧠 LeetCode Review Automator

> Paste a LeetCode problem link. Get a fully written Obsidian note with AI analysis. You only write your reflection.

---

## The Problem

After solving a LeetCode problem, reviewing it properly takes time:
- Copy your code
- Paste it into an AI with a detailed prompt
- Copy the analysis
- Create an Obsidian note
- Paste everything in
- Format it properly

Multiply that by dozens of problems per week and it becomes a workflow bottleneck.

## The Solution

bash
python main.py "https://leetcode.com/problems/two-sum/"

One command. The tool handles everything else.

---

## What gets generated

Every note is automatically filled with:

- ✅ Your latest submission code
- ✅ Time & space complexity analysis
- ✅ Optimization review
- ✅ Best known solution with clean commented code
- ✅ Learning takeaways and patterns to recognize
- ✅ Short reviews of your older attempts
- ✅ Problem metadata (date, submission count, tags)
- ✅ NeetCode video field (left empty if video exists, "No video" if not)
- ⬜ Your personal reflection — the only part you write

---

## Demo
```bash
========================================
   LeetCode Review Automator
   Processing 1 problem(s)
========================================

[1/3] Parsing problem URL...
       Slug: two-sum

[2/3] Fetching problem info...
       Title: 1. Two Sum
       Tags : ['LeetCode', 'Array', 'Hash Table']

[3/3] Fetching submissions...
       Total: 6 | Accepted: 5 | Date: 2026-02-10
       Fetching code 1/3...
       Fetching code 2/3...
       Fetching code 3/3...

[AI] Running full review on latest submission...
[AI] Running light review on older submission 1...
[AI] Running light review on older submission 2...

[NOTE] Generating Obsidian note...

========================================
  ✅ Done!
  /home/joe/Desktop/vault 2.0/LeetCode/1. Two Sum.md
========================================
```
---

## Requirements

- Python 3.12+
- Ubuntu / Linux (or WSL on Windows)
- An Obsidian vault
- A LeetCode account with at least one submission
- A free [OpenRouter](https://openrouter.ai) API key

---

## Setup

### 1. Clone the repository

bash
git clone https://github.com/YOUR_USERNAME/leetcode-reviewer.git
cd leetcode-reviewer

### 2. Create and activate a virtual environment

bash
python3 -m venv venv
source venv/bin/activate

You should see `(venv)` at the start of your terminal prompt. You need to run this activation command every time you open a new terminal.

### 3. Install dependencies

bash
pip install -r requirements.txt

### 4. Configure your Obsidian vault path

Open `config.py` and update this line to point to your LeetCode folder inside your vault:

python
OBSIDIAN_VAULT_PATH = "/home/YOUR_USERNAME/path/to/vault/LeetCode"

If the folder doesn't exist yet, the tool will create it automatically.

### 5. Get your LeetCode session cookies

The tool uses LeetCode's internal API — no browser automation. It authenticates using session cookies from your browser.

1. Go to [leetcode.com](https://leetcode.com) and log in
2. Press `F12` to open Developer Tools
3. Go to the **Application** tab (Firefox: **Storage** tab)
4. Click **Cookies** → `https://leetcode.com`
5. Find and copy the values for:
   - `LEETCODE_SESSION` — a very long string
   - `csrftoken` — a shorter string

> **Note:** These cookies expire every few weeks. If you get authentication errors, come back and refresh them.

### 6. Get a free OpenRouter API key

1. Sign up at [openrouter.ai](https://openrouter.ai) — no credit card needed
2. Go to [openrouter.ai/keys](https://openrouter.ai/keys)
3. Click **Create Key** and copy it

### 7. Create your `.env` file

bash
cp .env.example .env

Open `.env` and fill in your values:

LEETCODE_SESSION=paste_your_value_here
LEETCODE_CSRF=paste_your_csrftoken_here
OPENROUTER_API_KEY=paste_your_key_here

No spaces around `=`. No quotes around the values.

### 8. Test it

bash
python main.py "https://leetcode.com/problems/two-sum/"
`
Open your Obsidian vault — the note should be there.

---

## Usage

### Single problem

python main.py "https://leetcode.com/problems/two-sum/"
### Multiple problems at once

python main.py \
  "https://leetcode.com/problems/two-sum/" \
  "https://leetcode.com/problems/valid-anagram/" \
  "https://leetcode.com/problems/contains-duplicate/"
### From a file (best for bulk review)

Create urls.txt in the project folder:

# Arrays & Hashing
https://leetcode.com/problems/two-sum/
https://leetcode.com/problems/valid-anagram/
https://leetcode.com/problems/contains-duplicate/

# Two Pointers
https://leetcode.com/problems/valid-palindrome/
https://leetcode.com/problems/3sum/
Lines starting with # are treated as comments. Then run:

python main.py --file urls.txt
---

## Project structure
```
leetcode-reviewer/
│
├── main.py                 # Entry point — run this
├── config.py               # Vault path and settings
├── neetcode.py             # NeetCode video lookup
├── neetcode_slugs.txt      # All NeetCode problem slugs
│
├── scraper/
│   └── submissions.py      # LeetCode GraphQL API calls
│
├── ai/
│   └── reviewer.py         # AI review prompts and parsing
│
├── notes/
│   └── generator.py        # Obsidian markdown generator
│
├── .env.example            # Template — copy this to .env
├── requirements.txt        # Python dependencies
└── .gitignore
---
```

## Troubleshooting

| Error | Fix |
|---|---|
| Missing LEETCODE_SESSION or LEETCODE_CSRF | Your .env file is missing or has wrong variable names |
| LeetCode API returned status 403 | Your session cookies expired — refresh them from DevTools |
| No submissions found | You haven't submitted this problem on LeetCode yet |
| ModuleNotFoundError | Run source venv/bin/activate then pip install -r requirements.txt |
| (venv) not showing | Run source venv/bin/activate before any other command |

---

## How the NeetCode field works

The tool checks if each problem is part of the NeetCode problem set:

- In the list → NeetCode field is left blank — paste the video link yourself
- Not in the list → NeetCode field shows "No video"

---

## Built with

- [Playwright](https://playwright.dev/) — not used (switched to direct API)
- [LeetCode GraphQL API](https://leetcode.com/graphql) — fetches submissions
- [OpenRouter](https://openrouter.ai) — AI routing (currently using Gemini 2.5 Flash)
- [Obsidian](https://obsidian.md) — note destination

---

## Contributing

Pull requests are welcome. If LeetCode's API changes and something breaks, open an issue and paste the full terminal output.
---