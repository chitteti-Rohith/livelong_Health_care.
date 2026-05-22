"""
utils/chatbot.py  [LiveLong AI v3]
------------------------------------
Context-aware, human-like chatbot.
Session context is always checked first before static rules.
"""
import re

CARE_LABELS = {
    "home": "Home Care", "govt": "Government Hospital",
    "clinic": "Nearby Clinic", "private": "Private Hospital",
}

RULES = [
    (r"\b(hi|hello|hey|namaste|namaskar)\b",
     "Hello! 👋 I'm LiveLong AI — your personal healthcare decision guide.\n"
     "Use the form above to analyse your symptoms, then ask me anything about your result, costs, or alternatives!"),
    (r"\b(emergency|ambulance|108|dying|heart attack|stroke)\b",
     "🚨 This sounds like an emergency! Call **108** (free ambulance, 24/7) immediately. "
     "Go to the nearest Government Hospital Emergency Ward. Do not wait."),
    (r"\b(ayushman|pmjay|pm.jay|health card|golden card)\b",
     "**Ayushman Bharat (PM-JAY)** offers free hospitalisation up to ₹5 lakh/year for eligible families. "
     "Check eligibility at pmjay.gov.in — most government hospitals and many empanelled private hospitals accept this card at zero cost."),
    (r"\b(government|govt|sarkari|free hospital)\b",
     "Government hospitals in India provide subsidised or free treatment. They are your best option when budget is limited. "
     "Quality care is available — AIIMS, KEM, Osmania and others have excellent facilities."),
    (r"\b(private hospital|private care)\b",
     "Private hospitals offer faster service, better amenities, and shorter wait times — but cost significantly more. "
     "Our cost estimator shows you the exact range so you can make an informed decision."),
    (r"\b(dengue|platelet|bone pain)\b",
     "Dengue warning signs: high fever + severe joint/bone pain + rash + low platelet count.\n"
     "➤ Do NOT take aspirin or ibuprofen — only paracetamol.\n"
     "➤ Get an NS1 antigen test at any government hospital.\n"
     "➤ If platelets drop below 50,000, hospitalisation is required immediately."),
    (r"\b(diabetes|blood sugar|sugar level)\b",
     "Diabetes symptoms include excessive thirst, frequent urination, blurry vision, and sudden weight loss. "
     "A fasting blood sugar test costs ₹50–200 at a government clinic. Early diagnosis significantly improves outcomes."),
    (r"\b(home remedy|self.care|treat at home)\b",
     "For mild symptoms, home care is practical:\n"
     "• Fever/pain → Paracetamol (avoid aspirin for children)\n"
     "• Dehydration → ORS sachets\n"
     "• Cold/cough → Steam, warm fluids, rest\n"
     "• Rash → Calamine lotion or antihistamine\n"
     "⚠️ If no improvement in 48 hours, please visit a clinic."),
    (r"\b(fever|high temperature)\b",
     "Fever guidance:\n• Below 38.5°C → rest + paracetamol + fluids\n"
     "• 38.5–39.5°C → visit clinic within 24 hours\n• Above 39.5°C → emergency care immediately"),
    (r"\b(chest pain|chest tightness)\b",
     "🚨 Chest pain must never be ignored. It may indicate a cardiac event. "
     "Call **108** or go to the nearest emergency room right now. Every minute matters."),
    (r"\b(breathless|difficulty breathing|cant breathe)\b",
     "🚨 Difficulty breathing is a medical emergency. Call **108** immediately."),
    (r"\b(thank|thanks|shukriya)\b",
     "You're welcome! 😊 Stay healthy and don't hesitate to come back with any questions. Your wellbeing matters. 💙"),
    (r"\b(who are you|what is livelong|about)\b",
     "I'm **LiveLong AI** — an AI-powered healthcare decision intelligence platform built for India. "
     "I help you find the right care pathway, estimate costs, and navigate the healthcare system — all for free."),
    (r"\b(help|how to use|guide)\b",
     "How to use LiveLong AI:\n1️⃣ Describe your symptoms in the form\n2️⃣ Set your city and budget\n"
     "3️⃣ Click **Get Smart Recommendation**\n4️⃣ Ask me: 'explain my result', 'alternatives', 'how much does private cost?'"),
]


def _context_reply(msg: str, ctx: dict):
    severity    = ctx.get("severity", "low")
    care_type   = ctx.get("care_type", "govt")
    budget      = ctx.get("budget", 0)
    city        = ctx.get("city", "your city").title()
    condition   = ctx.get("condition")
    costs       = ctx.get("costs", {})
    alternatives= ctx.get("alternatives", [])
    explanation = ctx.get("explanation", "")
    budget_analysis = ctx.get("budget_analysis", {})
    is_emergency    = ctx.get("is_emergency", False)
    confidence      = ctx.get("confidence", 0.0)
    human_advice    = ctx.get("human_advice", "")
    risk_insight    = ctx.get("risk_insight", "")

    cname = condition["name"] if condition else "your symptoms"
    label = CARE_LABELS.get(care_type, care_type.title())
    conf_str = f"Confidence: {confidence}" if confidence else ""

    # explain / why / reason
    if re.search(r"\b(why|explain|reason|tell me more|how did you|what does this mean)\b", msg):
        base = explanation if explanation else f"Based on your symptoms pointing toward {cname}, {label} is the most suitable suggestion."
        suffix = f"\n\n{human_advice}" if human_advice else ""
        return f"{base}{suffix}"

    # cost / price / how much
    if re.search(r"\b(cost|how much|price|expensive|afford|budget breakdown)\b", msg):
        if not costs:
            return "Cost data isn't available for your condition yet. Please check with a local hospital directly."
        lines = [f"💸 Cost breakdown for **{cname}** in {city}:\n"]
        for care in ["home", "govt", "clinic", "private"]:
            if care not in costs:
                continue
            c  = costs[care]
            ba = budget_analysis.get(care, {})
            tag = "✅" if ba.get("affordable") else f"❌ +₹{ba.get('shortfall',0):,}"
            star = " ← **Suggested**" if care == care_type else ""
            lines.append(f"• **{CARE_LABELS[care]}**: ₹{c['min']:,} – ₹{c['max']:,}  {tag}{star}")
        lines.append(f"\nYour budget: ₹{budget:,}")
        return "\n".join(lines)

    # alternatives
    if re.search(r"\b(alternative|other option|different|instead|another choice|other hospital)\b", msg):
        if not alternatives:
            return f"Given your symptoms and budget, **{label}** is the most appropriate pathway. No strong alternatives available at this time."
        lines = [f"🔀 Other options for **{cname}**:\n"]
        for alt in alternatives[:3]:
            tag = "✅ Affordable" if alt.get("affordable") else f"⚠️ Need ₹{alt.get('shortfall',0):,} more"
            lines.append(f"• **{alt['label']}** — {tag}\n  {alt['reason']}")
        return "\n".join(lines)

    # private cost
    if re.search(r"\b(private|corporate hospital|apollo|fortis|max)\b", msg):
        if "private" in costs:
            c  = costs["private"]
            ba = budget_analysis.get("private", {})
            if ba.get("affordable"):
                return (f"Private hospital for **{cname}** costs ₹{c['min']:,} – ₹{c['max']:,}. "
                        f"Your budget of ₹{budget:,} covers this — you'd have ₹{ba.get('surplus',0):,} to spare. "
                        f"Private care offers faster service and better amenities.")
            else:
                return (f"Private hospital for **{cname}** costs a minimum of ₹{c['min']:,}. "
                        f"This exceeds your current budget of ₹{budget:,} by ₹{ba.get('shortfall',0):,}. "
                        f"A government hospital or clinic would be more practical for you right now.")
        return "Private hospital cost data isn't available for this condition."

    # govt
    if re.search(r"\b(government|govt|sarkari|free)\b", msg):
        if "govt" in costs:
            c  = costs["govt"]
            ba = budget_analysis.get("govt", {})
            return (f"Government hospital care for **{cname}** costs ₹{c['min']:,} – ₹{c['max']:,}. "
                    f"{ba.get('verdict','')}. This covers: {c['includes']}. "
                    f"Ayushman Bharat cardholders may receive this care for free.")

    # risk / future / worsen
    if re.search(r"\b(risk|worsen|future|what if|danger|serious|precaution)\b", msg):
        return risk_insight if risk_insight else f"Monitor {cname} closely. If symptoms worsen within 48 hours, visit a doctor immediately."

    # recommend / suggest / should I go
    if re.search(r"\b(recommend|suggest|should i|which hospital|best option|where to go)\b", msg):
        return (
            f"Based on your analysis:\n"
            f"• **Possible match:** {cname}  ({conf_str})\n"
            f"• **Severity:** {severity.upper()}\n"
            f"• **Budget:** ₹{budget:,}\n"
            f"• **Suggested pathway:** {label} in {city}\n\n"
            f"{human_advice}"
        )

    return None


def get_chatbot_response(user_message: str, context: dict = None) -> str:
    msg = user_message.strip().lower()

    if context:
        reply = _context_reply(msg, context)
        if reply:
            return reply

    for pattern, response in RULES:
        if re.search(pattern, msg, re.IGNORECASE):
            return response

    # Smart fallback with context
    if context:
        cname = (context.get("condition") or {}).get("name", "your condition")
        label = CARE_LABELS.get(context.get("care_type","govt"), "Government Hospital")
        return (
            f"Based on your current analysis for **{cname}**, I suggested **{label}**.\n"
            f"You can ask me:\n"
            f"• 'explain my result'\n• 'what are my alternatives?'\n"
            f"• 'how much does private hospital cost?'\n• 'what are the risks if I wait?'\n"
            f"For emergencies, always call **108**. 💙"
        )

    return ("I'm here to help with healthcare guidance! Ask me about:\n"
            "• Your analysis result — run the form above first\n"
            "• Govt vs private hospital costs\n• Ayushman Bharat scheme\n"
            "• Home remedies for common conditions\n• Emergency numbers\n"
            "For emergencies, call **108** immediately. 💙")
