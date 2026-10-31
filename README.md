# LangGraph Learning

A hands-on learning journal for Python, LangChain, and LangGraph. This repository
will collect small experiments, useful notes, and working examples as I learn.

## Learning log

Add a dated entry when you learn or build something. Keep each entry specific:

```text
## YYYY-MM-DD — Topic
- Learned:
- Built or tried:
- Next:
```

## Getting started

Create and activate a virtual environment in PowerShell:

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell activation is restricted by your organization, use Command Prompt:

```bat
.venv\Scripts\activate.bat
```

## Branch workflow

- `main` is the stable, reviewed learning portfolio.
- `learning` is the ongoing branch for daily experiments and notes.
- For a larger standalone project, create a short-lived branch such as
  `feature/tool-calling-demo` from `learning`, then merge it back when ready.

Start or return to the daily learning branch:

```powershell
git switch learning
```

After making a real learning update, review, commit, and push it:

```powershell
git status
git add README.md
git commit -m "docs: record learning progress"
git push -u origin learning
```

Add the files you actually changed instead of blindly staging everything. Never
commit virtual environments, API keys, or `.env` files.

When a set of changes is ready for the portfolio, open a pull request from
`learning` into `main` on GitHub and merge it after reviewing the diff.
