# AI-Assist

**Conversational IT Helpdesk Triage and Troubleshooting Assistant**

## Current features
- Teacher enters an IT support issue in natural language.
- System identifies category, priority, and issue type.
- Assistant provides one troubleshooting step at a time.
- Teacher replies **Solved** or **Not solved**.
- Unresolved cases are escalated to IT.
- Vague requests trigger clarification instead of guessing.

## Run on Windows

```bat
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Demo cases

### Urgent Microsoft Teams
`I cannot access Microsoft Teams and my class starts in 15 minutes.`

### Printer
`The staff room printer is showing a paper jam error.`

### Fallback
`Laptop problem`

## Run tests

```bat
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

## Important limitation
This repository is the current conversational prototype. The final Generative AI + RAG layer can be connected in the next stage. The present version uses a local troubleshooting knowledge base so the system is stable and demonstrable without paid API access.


## v2 improvements
- Fixed `Not solved` so it always moves to the next troubleshooting step.
- Added **Solved / Not solved / Escalate to IT** quick-response buttons.
- Power-related laptop issues start with relevant power checks instead of repeating a clarification question.
- Device power failure is treated as at least Medium priority unless a stronger urgency signal makes it High.
