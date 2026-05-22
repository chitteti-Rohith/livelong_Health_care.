"""
utils/decision_engine.py  [LiveLong AI v3]
-------------------------------------------
Decision Intelligence Engine

v3 additions:
  ✅ Confidence Score (symptom match strength + data quality)
  ✅ Cost Breakdown (consult / medicine / tests / stay)
  ✅ Hospital Ranking (rating + budget fit + type priority)
  ✅ Top-3 hospital recommendations with reason strings
  ✅ Human-like advice line ("If I were you…")
  ✅ Future risk insight ("If symptoms worsen…")
  ✅ Conversational explanation (non-robotic)
  ✅ Provider transparency (distance, ranking reason)
  ✅ Responsible AI language (suggestion / recommendation only)
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database.db import get_connection

SEVERITY_ORDER = {"low": 1, "medium": 2, "critical": 3}
CARE_PRIORITY  = ["home", "govt", "clinic", "private"]

CARE_LABELS = {
    "home":    "Home Care",
    "govt":    "Government Hospital",
    "clinic":  "Nearby Clinic",
    "private": "Private Hospital",
}

EMERGENCY_KEYWORDS = [
    "chest pain", "chest pressure", "chest tightness",
    "can't breathe", "cannot breathe", "cant breathe",
    "difficulty breathing", "shortness of breath", "breathless",
    "heart attack", "stroke", "unconscious", "fainted", "fainting",
    "bleeding heavily", "coughing blood", "blood in stool",
    "seizure", "convulsion", "paralysis", "sudden numbness",
    "severe headache", "worst headache", "thunderclap",
]


# ── Emergency Detection ──────────────────────────────────────────────────────

def detect_emergency(symptoms_text: str, severity: str):
    text_lower = symptoms_text.lower()
    trigger = next((kw for kw in EMERGENCY_KEYWORDS if kw in text_lower), None)
    if not trigger and severity != "critical":
        return None
    reason = f"keyword '{trigger}' detected" if trigger else "severity rated as CRITICAL"
    return {
        "is_emergency": True, "trigger": reason,
        "message": (
            "🚨 EMERGENCY SITUATION DETECTED\n"
            "Your reported symptoms suggest a potentially life-threatening condition.\n"
            "➤ Call 108 immediately — free ambulance, available 24 hours\n"
            "➤ Go to the nearest Government Hospital Emergency Ward\n"
            "➤ Do not drive — have someone escort you\n"
            "➤ Budget is not a consideration — getting care is the priority"
        ),
        "care_type": "govt", "override": True,
    }


# ── Symptom Matching ─────────────────────────────────────────────────────────

def match_symptoms(user_input: str) -> list:
    user_text = user_input.lower()
    conn = get_connection()
    all_syms = conn.execute("SELECT * FROM symptoms").fetchall()
    conn.close()
    matched, seen = [], set()
    for sym in all_syms:
        kws = [k.strip() for k in sym["keywords"].split(",")] + [sym["name"].replace("_", " ")]
        for kw in kws:
            if kw and kw in user_text and sym["id"] not in seen:
                matched.append(dict(sym))
                seen.add(sym["id"])
                break
    return matched

def get_overall_severity(matched: list) -> str:
    if not matched:
        return "low"
    worst = "low"
    for s in matched:
        if SEVERITY_ORDER.get(s["severity"], 0) > SEVERITY_ORDER.get(worst, 0):
            worst = s["severity"]
    return worst


# ── Condition Matching ───────────────────────────────────────────────────────

def match_condition(matched: list):
    if not matched:
        return None
    mids = set(str(s["id"]) for s in matched)
    conn = get_connection()
    conds = conn.execute("SELECT * FROM conditions").fetchall()
    conn.close()
    best, best_score = None, 0
    for c in conds:
        score = len(mids & set(c["symptom_ids"].split(",")))
        if score > best_score:
            best_score, best = score, dict(c)
    return best


# ── Confidence Score ─────────────────────────────────────────────────────────

def calc_confidence(matched: list, condition, costs: dict) -> float:
    """
    Confidence = weighted average of:
      - Symptom match ratio   (40%): matched symptoms / avg condition size
      - Data completeness     (30%): cost types available / 4
      - Specificity           (30%): critical/medium symptoms boost score
    Range: 0.0 – 1.0
    """
    if not matched:
        return 0.20

    # Symptom match component
    total_symptoms   = max(len(matched), 1)
    match_ratio      = min(total_symptoms / 4.0, 1.0)   # cap at 4 symptoms = 1.0

    # Data completeness
    data_score = len(costs) / 4.0

    # Specificity: critical/medium symptoms are stronger signals
    spec = sum(1 for s in matched if s["severity"] in ("medium", "critical"))
    spec_score = min(spec / max(total_symptoms, 1), 1.0)

    confidence = (0.40 * match_ratio) + (0.30 * data_score) + (0.30 * spec_score)
    return round(min(max(confidence, 0.20), 0.97), 2)


# ── Cost Ranges ──────────────────────────────────────────────────────────────

def get_cost_ranges(condition_id: int) -> dict:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM cost_ranges WHERE condition_id=?", (condition_id,)).fetchall()
    conn.close()
    return {
        r["care_type"]: {
            "min": r["min_cost"], "max": r["max_cost"], "includes": r["includes"],
            "consult": r["consult_cost"], "medicine": r["medicine_cost"],
            "tests": r["test_cost"],      "stay": r["stay_cost"],
        }
        for r in rows
    }


# ── Cost Breakdown ───────────────────────────────────────────────────────────

def build_cost_breakdown(costs: dict, care_type: str) -> dict:
    """Return itemised cost breakdown for the recommended care type."""
    c = costs.get(care_type)
    if not c:
        return {}
    items = []
    if c["consult"]:  items.append({"label": "Consultation Fee",    "amount": c["consult"]})
    if c["medicine"]: items.append({"label": "Medicines / Pharmacy","amount": c["medicine"]})
    if c["tests"]:    items.append({"label": "Tests / Diagnostics", "amount": c["tests"]})
    if c["stay"]:     items.append({"label": "Hospital Stay",       "amount": c["stay"]})
    total = sum(i["amount"] for i in items)
    return {
        "items":      items,
        "estimated":  total if total else c["min"],
        "range_min":  c["min"],
        "range_max":  c["max"],
        "care_type":  care_type,
        "label":      CARE_LABELS.get(care_type, care_type),
    }


# ── Budget Analysis ──────────────────────────────────────────────────────────

def build_budget_analysis(budget: int, costs: dict) -> dict:
    analysis = {}
    for care, c in costs.items():
        affordable = budget >= c["min"]
        shortfall  = max(0, c["min"] - budget)
        surplus    = max(0, budget - c["min"])
        verdict    = (f"✅ Affordable — ₹{surplus:,} to spare"
                      if affordable else
                      f"❌ Exceeds budget by ₹{shortfall:,}")
        analysis[care] = {
            "affordable": affordable, "shortfall": shortfall,
            "surplus": surplus, "verdict": verdict,
            "min": c["min"], "max": c["max"], "includes": c["includes"],
        }
    return analysis


# ── Care Type Selection ───────────────────────────────────────────────────────

def pick_care_type(severity: str, budget: int, costs: dict) -> str:
    priority = (["govt", "private"] if severity == "critical" else
                ["govt", "clinic", "private"] if severity == "medium" else
                ["home", "clinic", "govt", "private"])
    for care in priority:
        if care in costs and budget >= costs[care]["min"]:
            return care
    for care in CARE_PRIORITY:
        if care in costs:
            return care
    return "govt"


# ── Hospital Ranking (Top 3) ─────────────────────────────────────────────────

def get_ranked_hospitals(city: str, care_type: str, budget: int, costs: dict) -> list:
    """
    Fetch hospitals from DB and rank by:
      1. Type match (preferred care_type first)
      2. Budget affordability
      3. Rating (descending)
    Returns top 3 with a 'recommendation_reason' field.
    """
    city_clean = city.strip().lower()
    conn = get_connection()

    # Fetch broader pool for ranking
    if care_type == "home":
        rows = conn.execute(
            "SELECT * FROM hospitals WHERE city=? ORDER BY rating DESC LIMIT 10", (city_clean,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM hospitals WHERE city=? ORDER BY rating DESC LIMIT 10", (city_clean,)
        ).fetchall()
    conn.close()

    if not rows:
        return []

    # Score and rank
    def score(h):
        type_score   = 3 if h["type"] == care_type else (2 if care_type == "home" and h["type"] == "clinic" else 1)
        rating_score = h["rating"] / 5.0
        min_c        = costs.get(h["type"], {}).get("min", 9999999)
        budget_score = 1.0 if budget >= min_c else 0.3
        dist_score   = max(0, 1.0 - (h["distance_km"] / 15.0))
        return (type_score * 0.40) + (rating_score * 0.30) + (budget_score * 0.20) + (dist_score * 0.10)

    hospitals = [dict(h) for h in rows]
    hospitals.sort(key=score, reverse=True)
    top3 = hospitals[:3]

    # Add recommendation reason
    TYPE_STRENGTHS = {"govt": "affordable", "private": "premium care", "clinic": "convenient"}
    for h in top3:
        reasons = []
        if h["type"] == care_type:
            reasons.append("matches recommended care type")
        if budget >= costs.get(h["type"], {}).get("min", 9999999):
            reasons.append("within your budget")
        else:
            reasons.append("may need additional budget")
        if h["rating"] >= 4.3:
            reasons.append("highly rated")
        if h["distance_km"] <= 3.0:
            reasons.append("conveniently nearby")
        reasons.append(TYPE_STRENGTHS.get(h["type"], "suitable care"))
        h["recommendation_reason"] = "Chosen due to " + ", ".join(reasons[:3])

    return top3


# ── Alternatives ──────────────────────────────────────────────────────────────

def build_alternatives(severity: str, budget: int, costs: dict, recommended: str) -> list:
    REASONING = {
        "home":    "Rest and over-the-counter medicine can manage mild symptoms at home. Monitor for 48 hours.",
        "govt":    "Government hospitals provide subsidised or free treatment — ideal when budget is limited. PM-JAY cardholders may get free care.",
        "clinic":  "A local clinic offers faster consultation than a large hospital, suitable for moderate symptoms.",
        "private": "Private hospitals provide faster service and better amenities if your budget allows.",
    }
    alternatives = []
    for care in ["home", "govt", "clinic", "private"]:
        if care == recommended or care not in costs:
            continue
        if care == "home" and severity == "critical":
            continue
        c = costs[care]
        alternatives.append({
            "care_type": care, "label": CARE_LABELS[care],
            "reason": REASONING.get(care, ""),
            "affordable": budget >= c["min"],
            "min": c["min"], "max": c["max"],
            "includes": c["includes"],
            "shortfall": max(0, c["min"] - budget),
        })
    if severity == "low" and recommended != "home":
        alternatives.insert(0, {
            "care_type": "delayed", "label": "⏳ Monitor at Home (1–2 days)",
            "reason": "Since severity is low, you can safely monitor at home for 1–2 days. Take OTC medicine and rest. Visit a doctor if symptoms worsen.",
            "affordable": True, "min": 0, "max": 400, "includes": "OTC medicine + rest", "shortfall": 0,
        })
    return alternatives


# ── Human-like Advice & Risk Insight ─────────────────────────────────────────

def build_human_advice(severity: str, care_type: str, condition, budget: int) -> str:
    """Generates a warm, first-person advisory line."""
    cname = condition["name"] if condition else "your reported condition"
    label = CARE_LABELS.get(care_type, care_type)

    if severity == "critical":
        return (f"If I were in your situation, I would not wait — {cname} with these symptoms "
                f"requires immediate attention. Please head to the emergency ward or call 108 right now.")
    elif severity == "medium":
        return (f"If I were you, I would visit a {label.lower()} within the next 24 hours. "
                f"For {cname}, early professional care makes a significant difference in recovery time.")
    else:
        return (f"If I were you, I'd start with {label.lower()} for now — your condition appears mild "
                f"and your budget of ₹{budget:,} is well-suited for this option. "
                f"Rest well and monitor how you feel over the next day or two.")

def build_risk_insight(severity: str, condition, care_type: str) -> str:
    """Future risk / follow-up guidance."""
    cname = condition["name"] if condition else "your condition"
    if severity == "critical":
        return "⚠️ Do not delay care. Conditions like this can deteriorate rapidly without medical intervention."
    elif severity == "medium":
        return (f"⚠️ If symptoms of {cname} persist for more than 2–3 days, or if you develop "
                f"new symptoms like high fever or breathlessness, please visit a hospital immediately.")
    else:
        return (f"💡 If {cname} symptoms worsen or do not improve within 48 hours of home care, "
                f"consider visiting a clinic. Early intervention prevents complications.")


# ── Explanation (Conversational) ─────────────────────────────────────────────

def build_explanation(severity: str, care_type: str, condition,
                       budget: int, budget_analysis: dict, is_emergency: bool) -> str:
    cname = condition["name"] if condition else "your reported symptoms"
    label = CARE_LABELS.get(care_type, care_type)

    if is_emergency:
        return (f"So, looking at your symptoms, this appears to match {cname} — a situation that "
                f"needs immediate medical attention. In cases like this, we always prioritise getting you "
                f"to an emergency ward first. Budget can be sorted out later; your safety comes first.")

    sev_phrase = {
        "low":      "which is on the milder end",
        "medium":   "which needs timely attention",
        "critical": "which is quite serious",
    }.get(severity, "")

    ba    = budget_analysis.get(care_type, {})
    aff   = ba.get("affordable", True)
    surp  = ba.get("surplus", 0)
    short = ba.get("shortfall", 0)

    budget_phrase = (
        f"your budget of ₹{budget:,} covers this comfortably, with ₹{surp:,} to spare"
        if aff else
        f"this is the most affordable option available to you given your ₹{budget:,} budget"
    )

    return (
        f"So, based on your symptoms, this looks like it could be related to {cname} — {sev_phrase}. "
        f"Given the severity and {budget_phrase}, {label} is the safest and most practical suggestion "
        f"for your situation right now. This is a decision-support recommendation, not a diagnosis."
    )


# ── Cost Comparison ───────────────────────────────────────────────────────────

def build_cost_comparison(costs: dict, recommended: str, budget: int) -> list:
    rows = []
    for care in CARE_PRIORITY:
        if care not in costs:
            continue
        c = costs[care]
        rows.append({
            "care_type": care, "label": CARE_LABELS[care],
            "min": c["min"], "max": c["max"], "includes": c["includes"],
            "affordable": budget >= c["min"],
            "shortfall": max(0, c["min"] - budget),
            "is_recommended": care == recommended,
        })
    return rows


# ── Recommendation Text ───────────────────────────────────────────────────────

def build_recommendation_text(severity: str, care_type: str, condition,
                               costs: dict, budget: int, is_emergency: bool) -> str:
    if is_emergency:
        return ("🚨 Immediate emergency care suggested.\n"
                "Call 108 (free ambulance) right now.\n"
                "Head to the nearest Government Hospital Emergency Ward.")
    urgency = {"critical": "🚨 Urgent care suggested.",
                "medium":   "⚠️ Professional consultation suggested within 24 hours.",
                "low":      "✅ Non-urgent — basic care is a reasonable first step."}.get(severity, "")
    cname = condition["name"] if condition else "General Symptoms"
    label = CARE_LABELS.get(care_type, care_type)
    cost  = f"Estimated cost: ₹{costs[care_type]['min']:,} – ₹{costs[care_type]['max']:,}" if care_type in costs else ""
    return f"{urgency}\nSuggested condition match: {cname}\nSuggested care pathway: {label}\n{cost}"


# ── MAIN ENGINE ───────────────────────────────────────────────────────────────

def run_engine(symptoms_text: str, city: str, budget: int) -> dict:
    matched      = match_symptoms(symptoms_text)
    severity     = get_overall_severity(matched)
    emergency    = detect_emergency(symptoms_text, severity)
    is_emergency = emergency is not None
    condition    = match_condition(matched)
    costs        = get_cost_ranges(condition["id"]) if condition else {}
    care_type    = "govt" if is_emergency else pick_care_type(severity, budget, costs)

    confidence       = calc_confidence(matched, condition, costs)
    budget_analysis  = build_budget_analysis(budget, costs)
    alternatives     = build_alternatives(severity, budget, costs, care_type)
    explanation      = build_explanation(severity, care_type, condition, budget, budget_analysis, is_emergency)
    cost_comparison  = build_cost_comparison(costs, care_type, budget)
    cost_breakdown   = build_cost_breakdown(costs, care_type)
    hospitals        = get_ranked_hospitals(city, care_type, budget, costs)
    recommendation   = build_recommendation_text(severity, care_type, condition, costs, budget, is_emergency)
    human_advice     = build_human_advice(severity, care_type, condition, budget)
    risk_insight     = build_risk_insight(severity, condition, care_type)

    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO recommendations (symptoms_input,city,budget,severity_result,recommendation) VALUES(?,?,?,?,?)",
            (symptoms_text, city, budget, severity, recommendation)
        )
        conn.commit(); conn.close()
    except Exception:
        pass

    return {
        "matched_symptoms": matched,       "severity":        severity,
        "condition":        condition,     "costs":           costs,
        "care_type":        care_type,     "hospitals":       hospitals,
        "recommendation":   recommendation,"budget":          budget,
        "city":             city,          "symptoms_input":  symptoms_text,
        "is_emergency":     is_emergency,  "emergency":       emergency,
        "budget_analysis":  budget_analysis,"alternatives":   alternatives,
        "explanation":      explanation,   "cost_comparison": cost_comparison,
        "cost_breakdown":   cost_breakdown,"confidence":      confidence,
        "human_advice":     human_advice,  "risk_insight":    risk_insight,
    }
