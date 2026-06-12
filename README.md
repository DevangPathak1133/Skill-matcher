Skills Matching Website

This is a minimal Flask application that accepts job descriptions (JD) and resumes, extracts text, and scores matching using TF-IDF cosine similarity.

Quick start

1. Create and activate a Python virtual environment (Windows PowerShell shown):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the app:

```powershell
python app.py
```

4. Open http://127.0.0.1:5000 in your browser. Upload one or more JDs and resumes and click "Match".

Notes and next steps

- The extractor supports `.pdf`, `.docx`, and plain text files. PDF extraction uses `pdfminer.six` and `.docx` uses `python-docx`.
- Matching is a simple TF-IDF + cosine similarity approach; for production consider using named-entity recognition for skills, normalizing skill synonyms, and weighting resume sections differently.
- To improve: add authentication, async file handling, better error handling, and a persistent database for uploaded documents and results.
