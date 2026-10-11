# AI tool notes — complete honestly after testing

1. Tool used: [Claude AI chat].
2. I used AI for: [setting up and running the scraper locally on Windows. This covered getting Python 3.12 working (PATH, Microsoft Store alias, winget), creating the virtual environment, installing requirements, running scraper.py, and diagnosing the OpenAI 401 error caused by placeholder keys in .env. I ran it with --no-llm and it wrote 3 records to data\bonuses.json. I did not use AI to write the scraper code itself.
].
3. One thing it got wrong: [It had me run pip install in the outer folder, but requirements.txt was in the nested casino-bonus-scraper folder.
].
4. How I caught it: [The commands failed with errors in the terminal. A file search (Get-ChildItem) found no real install until I reinstalled with winget, and the VS Code Explorer showed the nested folder structure.
].
5. What I changed: [I reinstalled Python with winget, created the venv using the full path to python.exe, ran pip install from the inner folder, and ran the scraper with --no-llm.
].

Time spent: [17:30 to 19:20].
