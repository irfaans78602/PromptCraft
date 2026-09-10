# PromptCraft v2 — Niche-driven

A small web app: pick a niche, fill in Role / Context / Task / Format-Tone,
submit, and get a Gemini-generated response you can copy.

## What's new in v2

One dropdown ("Niche") drives everything else:
- **SQL Query / Schema Assistant**
- **ETL Error Translator**
- **Architecture Doc Generator**
- **Resume Repositioning**
- **Cloud Cost Report Narrator**

Selecting a niche pre-fills the Role field, swaps the Task field to a
dropdown of niche-relevant sub-tasks, changes the Context placeholder text,
and sets a sensible Format/Tone default — all editable. Behind the scenes,
each niche also has hidden "system instructions" that get added to the
prompt sent to Gemini, so the model responds with the right domain
expertise (e.g. correct T-SQL syntax for the SQL niche).

All niche config lives in one place in `app.py` (the `NICHES` dict).
Adding a 6th niche means adding one new dictionary entry — nothing else
in the backend or frontend needs to change, since the frontend builds its
dropdowns dynamically from `GET /niches`.

## Where the output appears

On the **same page**, directly below the form. There's no separate
results page — clicking "Generate" calls the backend, and the response
renders in a box under the button with a "Copy" button next to it.

## Setup

1. Get a **free** Gemini API key: https://aistudio.google.com/apikey
   (no credit card required)

2. Install dependencies:
   ```
   pip install -r requirements.txt --break-system-packages
   ```

3. Create a `.env` file in this folder:
   ```
   GEMINI_API_KEY=your_key_here
   ```

4. Run the app:
   ```
   uvicorn app:app --reload
   ```

5. Open http://127.0.0.1:8000 in your browser.

## Next steps (in order of learning value)

1. **Deploy it free** — Render.com or Railway both have free tiers for
   small FastAPI apps.
2. **Add Google Sign-In** — OAuth 2.0, resume-worthy on its own.
3. **Add a "save this prompt" feature** using your local MS SQL Server —
   store niche + four fields + result per user, keyed by niche.
4. **Only after that** — consider payments, based on real usage.
