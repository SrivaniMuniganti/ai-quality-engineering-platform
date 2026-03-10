# Demo Guide — AI Quality Engineering Platform

## Prerequisites
1. Python 3.11+
2. A Groq API key (free at https://console.groq.com)
3. Chrome/Chromium installed (Playwright handles this)

## Setup (5 minutes)

```bash
# 1. Clone & install
pip install -r requirements.txt
playwright install chromium

# 2. Configure environment
cp .env.example .env
# Edit .env — set GROQ_API_KEY

# 3. Launch
streamlit run app.py
```

Open http://localhost:8501 and log in (default: `admin` / `admin` unless changed in `.env`).

---

## Demo Walkthrough

### Step 1 — Dashboard (Page 1)
- Shows quality score, pass rate, and recent runs
- Empty on first run — metrics populate as you use the platform

### Step 2 — Requirements (Page 3)

**Option A: Manual Text**
1. Enter: *"Users must log in with valid credentials and see the inventory page"*
2. Click **Parse with AI**
3. A structured requirement appears in the list below

**Option B: Jira Simulation**
1. Click the **Jira Simulation** tab
2. Select *"SauceDemo Sprint 1"*
3. Preview 10 pre-built stories
4. Click **Import & Parse Stories with AI**
5. Watch 10 requirements get created automatically

**Option C: File Upload**
1. Click the **File Upload** tab
2. Upload `test-data/requirements.txt`
3. Click **Parse File with AI**

### Step 3 — Pipeline (Page 2)
- Click **Run Full Pipeline** to execute all stages end-to-end
- Watch Requirements → Test Cases → Scripts → Execution flow

### Step 4 — Test Cases (Page 4)
- Select a requirement and click **Generate Test Cases**
- AI produces 3–5 structured test cases with steps and expected results

### Step 5 — Scripts (Page 5)
- Select a test case and click **Generate Script**
- AI writes a complete Playwright pytest file
- Script is saved to `generated_tests/`

### Step 6 — Execution (Page 6)
- Select a script and click **Execute**
- Playwright runs the test headless against SauceDemo
- Results (pass/fail, duration, output) appear in the table

### Step 7 — Failure Analysis (Page 7)
- Select a failed test run and click **Analyse**
- AI identifies root cause, failure category, and suggests a fix

### Step 8 — Self-Healing (Page 8)
- Select a failed run and click **Attempt Self-Heal**
- Platform extracts the broken locator, queries the live DOM
- AI suggests alternative selectors
- Script is patched and re-executed automatically
- Healing result is saved to the database

### Step 9 — Dashboard Again (Page 1)
- Refresh to see updated quality score, execution trend, and healing stats

---

## Quick Test Run (No AI Required)

```bash
# Run all existing generated tests
pytest generated_tests/ -v --tb=short

# Run with HTML report
pytest generated_tests/ -v --html=reports/report.html --self-contained-html
```

---

## Key Demo Points

| Feature | Technology | Wow Factor |
|---|---|---|
| Requirement parsing | LangChain + LLM | Natural language → structured data |
| Test case generation | LangChain + LLM | Automated QA planning |
| Script generation | LangChain + LLM | Working Playwright code from spec |
| Test execution | Playwright + pytest | Real browser automation |
| Failure analysis | LangChain + LLM | AI root cause analysis |
| Self-healing | LangChain + Playwright | AI fixes broken tests automatically |
| Analytics | Plotly + pandas | Quality score & trend charts |

---

## Troubleshooting

| Issue | Fix |
|---|---|
| AI calls fail | Check `GROQ_API_KEY` in `.env`; test on page 3 Connection Test |
| Tests timeout | Ensure internet access to saucedemo.com; check `HEADLESS_BROWSER=true` |
| DB errors | Delete `data/qa_platform.db` and restart app |
| Import errors | Run `pip install -r requirements.txt` again |
