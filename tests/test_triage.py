
from src.triage import analyse_issue

def test_teams_case():
    r = analyse_issue("I cannot access Microsoft Teams and my class starts in 15 minutes.")
    assert r["category"] == "Microsoft 365 / Authentication"
    assert r["priority"] == "High"

def test_printer_case():
    r = analyse_issue("The staff room printer is showing a paper jam error.")
    assert r["category"] == "Printer"

def test_fallback_case():
    r = analyse_issue("Laptop problem")
    assert r["needs_clarification"] is True


def test_laptop_no_power_medium_priority():
    r = local_triage("Laptop is not turning on")
    assert r.category == "Hardware / Device"
    assert r.priority == "Medium"
