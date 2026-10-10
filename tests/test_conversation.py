
from src.conversation import reply_intent

def test_not_solved_is_negative():
    assert reply_intent("Not Solved") == "not_solved"

def test_still_not_working_is_negative():
    assert reply_intent("Still not working") == "not_solved"

def test_solved_is_positive():
    assert reply_intent("Solved") == "solved"

def test_escalate():
    assert reply_intent("Please escalate to IT") == "escalate"


from src.conversation import choose_steps

def test_power_failure_skips_generic_question():
    steps = choose_steps("Hardware / Device", "Laptop is not turning on")
    assert "charger" in steps[0].lower()
    assert "describe whether" not in steps[0].lower()
