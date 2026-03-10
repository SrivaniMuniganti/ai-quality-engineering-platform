# AI Quality Engineering Platform — Architecture

## Overview

A monolithic Streamlit application implementing an end-to-end AI-powered QA pipeline targeting [SauceDemo](https://www.saucedemo.com). The platform covers the full software testing lifecycle: Requirements → Test Cases → Scripts → Execution → Failure Analysis → Self-Healing.

## Technology Stack

| Layer | Technology |
|---|---|
| UI | Streamlit (multipage) |
| AI/LLM | LangChain LCEL + Groq (Llama 3.3 70B) / Anthropic / Google / Ollama |
| Database | SQLite (SQLAlchemy 2.x ORM) |
| Test Automation | Playwright + pytest |
| Reporting | pytest-html, pytest-json-report, Plotly |
| Target App | SauceDemo (https://www.saucedemo.com) |

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Streamlit UI (app.py)                       │
│  Pages: Dashboard | Pipeline | Requirements | Test Cases |        │
│         Scripts | Execution | Failure Analysis | Self-Healing    │
└────────────────────────┬────────────────────────────────────────┘
                         │
              ┌──────────▼──────────┐
              │    services/         │
              │  (business logic)    │
              └──────────┬──────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
   ┌──────────┐   ┌──────────┐  ┌──────────────┐
   │  chains/  │   │  core/   │  │ generated_   │
   │ (LCEL AI) │   │ (ORM/DB) │  │  tests/      │
   └──────────┘   └──────────┘  └──────────────┘
          │              │
          ▼              ▼
   ┌──────────┐   ┌──────────────┐
   │  LLM     │   │ SQLite DB    │
   │ Provider │   │ qa_platform  │
   └──────────┘   └──────────────┘
```

## Data Flow

```
User Input
  → pages/3_Requirements.py
  → services/requirement_service.py
  → chains/requirement_parser_chain.py  (LLM)
  → core/models.Requirement  (DB)

  → pages/4_Test_Cases.py
  → services/testcase_service.py
  → chains/testcase_generator_chain.py  (LLM)
  → core/models.TestCase  (DB)

  → pages/5_Scripts.py
  → services/script_service.py
  → chains/script_generator_chain.py  (LLM)
  → generated_tests/test_*.py  (files)
  → core/models.Script  (DB)

  → pages/6_Execution.py
  → services/execution_service.py
  → subprocess pytest  (Playwright)
  → core/models.TestRun  (DB)
  → reports/logs/run_*.json

  → pages/7_Failure_Analysis.py
  → chains/failure_analyzer_chain.py  (LLM)
  → core/models.Analysis  (DB)

  → pages/8_Self_Healing.py
  → services/healing_service.py
  → self_healing_engine/retry_engine.py
  → chains/self_healing_chain.py  (LLM)
  → core/models.HealingAttempt  (DB)
```

## Module Structure

### Core Layer (`core/`)
- `config.py` — Pydantic-Settings: reads `.env`, exposes `settings`
- `models.py` — SQLAlchemy ORM: Requirement, TestCase, Script, TestRun, Analysis, HealingAttempt
- `database.py` — SQLite engine + session factory + `init_db()`
- `security.py` — Input sanitisation, path traversal prevention

### AI Chains (`chains/`)
All chains follow the LCEL pattern: `prompt | get_llm() | StrOutputParser()`
- `requirement_parser_chain.py` — parses free text → structured requirements
- `testcase_generator_chain.py` — requirement → test cases
- `script_generator_chain.py` — test case → Playwright pytest script
- `failure_analyzer_chain.py` — failure output → root cause + fix
- `self_healing_chain.py` — broken locator + DOM context → alternative locators

### Services (`services/`)
Business logic layer; all functions return plain dicts, never ORM objects.
- `requirement_service.py`, `testcase_service.py`, `script_service.py`
- `execution_service.py` — subprocess pytest runner; persists TestRun; calls ResultCollector
- `healing_service.py` — orchestrates RetryEngine; exposes healing stats

### Self-Healing Engine (`self_healing_engine/`)
- `dom_analyzer.py` — extracts live DOM selectors via Playwright; falls back to static registry
- `locator_healer.py` — calls `self_healing_chain` to get alternative selectors
- `retry_engine.py` — full heal flow: parse → DOM → heal → patch → re-execute → persist

### Analytics (`qa_analytics_dashboard/`)
- `metrics_engine.py` — quality score, pass rate, failure distribution, execution trend
- `report_builder.py` — JSON/CSV report export
- `dashboard.py` — thin Streamlit wrapper

## Database Schema

```
Requirement (1) ──< TestCase (1) ──< Script (1) ──< TestRun (1) ──< Analysis
                                                           │
                                                           └──< HealingAttempt
```

## Security

- Script execution accepts only `script_id` (never a file path from user)
- `validate_script_path()` prevents path traversal outside `generated_tests/`
- `validate_generated_script()` ensures AI scripts start with `import`/`from`
- `sanitize_input()` strips prompt injection and limits input to 5000 chars

## AI Provider Configuration

Set `AI_PROVIDER` in `.env`:

| Value | Model | Requires |
|---|---|---|
| `groq` (default) | Llama 3.3 70B | `GROQ_API_KEY` |
| `anthropic` | Claude (configurable) | `ANTHROPIC_API_KEY` |
| `google` | Gemini 1.5 Flash | `GOOGLE_API_KEY` |
| `ollama` | Llama 3.1 (local) | Ollama running locally |
