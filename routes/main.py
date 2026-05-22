"""routes/main.py [LiveLong AI v3]"""
from flask import Blueprint, render_template, request, jsonify, session
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.decision_engine import run_engine
from utils.chatbot import get_chatbot_response

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")

@main.route("/analyse", methods=["POST"])
def analyse():
    data     = request.get_json(force=True)
    symptoms = data.get("symptoms", "").strip()
    city     = data.get("city", "").strip()
    budget   = int(data.get("budget", 0))
    if not symptoms: return jsonify({"error": "Please describe your symptoms."}), 400
    if not city:     return jsonify({"error": "Please select your city."}), 400
    if budget <= 0:  return jsonify({"error": "Please enter a valid budget (₹)."}), 400

    r = run_engine(symptoms, city, budget)

    session["last_result"] = {
        "severity": r["severity"], "care_type": r["care_type"],
        "budget": r["budget"], "city": r["city"],
        "condition": r["condition"], "costs": r["costs"],
        "is_emergency": r["is_emergency"], "emergency": r["emergency"],
        "budget_analysis": r["budget_analysis"], "alternatives": r["alternatives"],
        "explanation": r["explanation"], "confidence": r["confidence"],
        "human_advice": r["human_advice"], "risk_insight": r["risk_insight"],
    }

    return jsonify({
        "severity": r["severity"], "condition": r["condition"],
        "care_type": r["care_type"], "costs": r["costs"],
        "hospitals": r["hospitals"], "matched_symptoms": r["matched_symptoms"],
        "recommendation": r["recommendation"], "is_emergency": r["is_emergency"],
        "emergency": r["emergency"], "budget_analysis": r["budget_analysis"],
        "alternatives": r["alternatives"], "explanation": r["explanation"],
        "cost_comparison": r["cost_comparison"], "cost_breakdown": r["cost_breakdown"],
        "confidence": r["confidence"], "human_advice": r["human_advice"],
        "risk_insight": r["risk_insight"],
    })

@main.route("/chat", methods=["POST"])
def chat():
    data    = request.get_json(force=True)
    message = data.get("message", "").strip()
    if not message: return jsonify({"reply": "Please type a message!"}), 400
    reply = get_chatbot_response(message, session.get("last_result"))
    return jsonify({"reply": reply})

@main.route("/about")
def about():
    return render_template("about.html")
