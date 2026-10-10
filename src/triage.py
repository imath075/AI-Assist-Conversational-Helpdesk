
import re

CATEGORY_RULES = {
    "Microsoft 365 / Authentication": ["teams","microsoft 365","office 365","login","log in","sign in","password","mfa","authentication"],
    "Network / Wi-Fi": ["wifi","wi-fi","internet","network","disconnect","cannot connect"],
    "Printer": ["printer","print","printing","paper jam","queue","offline"],
    "Hardware / Device": ["laptop","desktop","computer","device","screen","battery","charger"],
    "Email": ["email","mail","mailbox","outlook"],
    "Software / Application": ["software","application","app","crash","error","not opening"]
}

HIGH_SIGNALS = ["class starts","lesson starts","exam","urgent","15 minutes","10 minutes","5 minutes","all users","service down"]
MEDIUM_SIGNALS = ["cannot access","cannot login","cannot log in","not working","unable to","error","disconnected","not turning on","won't turn on","will not turn on","no power","does not power on"]

def norm(text):
    return re.sub(r"\s+"," ",text.strip().lower())

def analyse_issue(text):
    t = norm(text)
    vague = {"problem","issue","help","not working","laptop problem","computer problem","pc problem","system problem"}
    if len(t.split()) < 3 or t in vague or len(t) < 15:
        return {
            "needs_clarification": True,
            "question": "Could you tell me which device or application is affected, what exactly happens, and whether you see an error message?"
        }

    best_cat, best_score = "General IT Support", 0
    for cat, kws in CATEGORY_RULES.items():
        score = sum(1 for k in kws if k in t)
        if score > best_score:
            best_cat, best_score = cat, score

    if any(x in t for x in HIGH_SIGNALS):
        priority = "High"
    elif any(x in t for x in MEDIUM_SIGNALS):
        priority = "Medium"
    else:
        priority = "Low"

    if any(x in t for x in ["login","log in","sign in","password","mfa"]):
        issue_type = "Authentication / Access"
    elif best_cat == "Network / Wi-Fi":
        issue_type = "Connectivity"
    elif best_cat == "Printer":
        issue_type = "Printing"
    elif best_cat == "Hardware / Device":
        issue_type = "Device / Hardware"
    else:
        issue_type = "General Support"

    return {
        "needs_clarification": False,
        "category": best_cat,
        "priority": priority,
        "issue_type": issue_type
    }
