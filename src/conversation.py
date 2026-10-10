
from src.triage import analyse_issue

KB = {
    "Microsoft 365 / Authentication": [
        "Please confirm that the device has a stable internet connection.",
        "Can you sign in to Microsoft 365 through a web browser?",
        "Please check whether your password or MFA was recently changed.",
        "Close Microsoft Teams completely and reopen it.",
        "If the problem continues, this should be escalated to the Microsoft 365 administrator."
    ],
    "Network / Wi-Fi": [
        "Please check whether Wi-Fi is enabled and you are connected to the correct school network.",
        "Can another nearby device connect to the same Wi-Fi?",
        "Please disconnect and reconnect to the Wi-Fi network.",
        "Restart the affected device if appropriate.",
        "If several users are affected, this should be escalated to IT."
    ],
    "Printer": [
        "Please check the printer display for a paper-jam or offline message.",
        "If paper is visibly jammed and safe to access, remove it carefully.",
        "Please check whether any print jobs are stuck in the queue.",
        "Restart the printer and try one test page.",
        "If the error remains, this should be escalated to IT."
    ],
    "Hardware / Device": [
        "Please describe whether this is a power, display, battery, or performance problem.",
        "Check the charger, power cable, battery, and visible device indicators.",
        "Restart the device if it is safe to do so.",
        "Record any exact error message.",
        "If the problem continues, this should be escalated for hardware diagnostics."
    ],
    "Email": [
        "Please confirm that the internet connection is working.",
        "Can you open your mailbox through the web version?",
        "Restart Outlook and try again.",
        "Check whether an error message is shown.",
        "If webmail also fails, this should be escalated to IT."
    ],
    "Software / Application": [
        "Please tell me the application name and exact error message.",
        "Close and reopen the application.",
        "Restart the device if appropriate.",
        "Check whether an approved update is pending.",
        "If the issue continues, escalate to IT."
    ],
    "General IT Support": [
        "Please provide the exact device/application and any error message.",
        "Please tell me when the issue started.",
        "Please confirm whether one user or several users are affected.",
        "If the problem cannot be identified safely, escalate to IT."
    ]
}

YES = {"yes", "solved", "fixed", "working now", "it works", "resolved", "yes solved"}
NO = {"no", "not solved", "still not working", "not fixed", "doesn't work", "did not work", "no not solved"}

def reply_intent(text):
    """Classify the teacher's short response safely.
    Negative responses are checked first so 'not solved' is never mistaken for 'solved'.
    """
    t = " ".join(text.strip().lower().split())

    # Check negative phrases first because strings like "not solved" contain "solved".
    if t in NO or any(phrase in t for phrase in [
        "not solved", "still not working", "not fixed",
        "doesn't work", "does not work", "did not work"
    ]):
        return "not_solved"

    if t in YES or any(phrase in t for phrase in [
        "working now", "it works", "problem solved", "issue resolved"
    ]):
        return "solved"

    if "escalate" in t or "technician" in t or "contact it" in t:
        return "escalate"

    return "other"


def choose_steps(category, issue):
    """Return troubleshooting steps tailored to details already supplied by the teacher."""
    steps = list(KB.get(category, KB["General IT Support"]))
    t = issue.strip().lower()

    # If the teacher already stated that a laptop/device will not power on,
    # skip the generic "describe the problem" question and start with power checks.
    if category == "Hardware / Device" and any(p in t for p in [
        "not turning on", "won't turn on", "will not turn on",
        "no power", "does not power on"
    ]):
        return [
            "Please disconnect any external accessories, then check that the charger is firmly connected and that the charging/power indicator is visible.",
            "If there is no indicator, try a known-good compatible charger or power outlet if one is available.",
            "Hold the power button for about 10 seconds, release it, then try to power on the laptop again.",
            "If the laptop still shows no power or display, this should be escalated to IT for hardware diagnostics."
        ]

    return steps

def reset_case(state):
    state.case = {
        "status":"new",
        "issue":"",
        "triage":{},
        "steps":[],
        "step_index":0,
        "history":[]
    }
    state.messages = [{
        "role":"assistant",
        "content":"Hello. Tell me what is not working, and I’ll guide you one step at a time."
    }]

def next_reply(user_text, case):
    t = user_text.strip().lower()

    if case["status"] == "new":
        result = analyse_issue(user_text)
        case["issue"] = user_text

        if result["needs_clarification"]:
            case["status"] = "clarifying"
            return result["question"]

        case["triage"] = {
            "category": result["category"],
            "priority": result["priority"],
            "issue_type": result["issue_type"]
        }
        case["steps"] = choose_steps(result["category"], case["issue"])
        case["step_index"] = 0
        case["status"] = "troubleshooting"
        return (
            f"I’ve identified this as **{result['category']}** with **{result['priority']} priority**.\n\n"
            f"**Step 1:** {case['steps'][0]}\n\n"
            "Did this solve the problem?"
        )

    if case["status"] == "clarifying":
        combined = case["issue"] + " " + user_text
        result = analyse_issue(combined)
        if result["needs_clarification"]:
            return result["question"]

        case["issue"] = combined
        case["triage"] = {
            "category": result["category"],
            "priority": result["priority"],
            "issue_type": result["issue_type"]
        }
        case["steps"] = choose_steps(result["category"], case["issue"])
        case["step_index"] = 0
        case["status"] = "troubleshooting"
        return (
            f"Thanks. I’ve classified this as **{result['category']}** with **{result['priority']} priority**.\n\n"
            f"**Step 1:** {case['steps'][0]}\n\n"
            "Did this solve the problem?"
        )

    if case["status"] == "troubleshooting":
        response_type = reply_intent(user_text)

        if response_type == "not_solved":
            case["step_index"] += 1
            if case["step_index"] < len(case["steps"]):
                n = case["step_index"] + 1
                step = case["steps"][case["step_index"]]
                if "escalated" in step.lower() or "escalate" in step.lower():
                    case["status"] = "escalated"
                    return (
                        f"{step}\n\n"
                        f"**Technician handover:** {case['triage']['category']} / "
                        f"{case['triage']['priority']} priority. Previous troubleshooting steps were attempted."
                    )
                return f"**Step {n}:** {step}\n\nDid this solve the problem?"

            case["status"] = "escalated"
            return "The available troubleshooting steps are complete. This should now be **escalated to IT**."

        if response_type == "solved":
            case["status"] = "resolved"
            return "Great. I’ll mark this as **resolved**."

        if response_type == "escalate":
            case["status"] = "escalated"
            return (
                f"This case will be **escalated to IT**.\n\n"
                f"**Technician handover:** {case['triage']['category']} / "
                f"{case['triage']['priority']} priority."
            )

        return "Please reply **Solved**, **Not solved**, or **Escalate to IT** so I can continue."

    if case["status"] == "resolved":
        return "This case is already resolved. Start a new support request for another issue."

    if case["status"] == "escalated":
        return "This case has already been escalated to IT."

    return "Please describe the problem again."
