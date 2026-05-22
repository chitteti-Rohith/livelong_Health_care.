/**
 * LiveLong AI – app.js v3
 * Full render pipeline: emergency · severity · decision · cost breakdown ·
 * comparison table · top-3 hospitals · alternatives · matched symptoms
 */

const CARE_LABELS = {
  home: "Home Care", govt: "Government Hospital",
  clinic: "Nearby Clinic", private: "Private Hospital", delayed: "Monitor at Home"
};
const CARE_ICONS = { home:"🏠", govt:"🏥", clinic:"🩺", private:"🏨", delayed:"⏳" };
const RANK_CLASSES = ["rank-gold","rank-silver","rank-bronze"];
const RANK_SYMBOLS = ["🥇","🥈","🥉"];

// ── Chip selection ─────────────────────────────────────────────────────────
document.querySelectorAll(".chip").forEach(chip => {
  chip.addEventListener("click", () => {
    const sym  = chip.dataset.sym;
    const ta   = document.getElementById("symptoms");
    const curr = ta.value.trim();
    if (curr.includes(sym)) {
      ta.value = curr.replace(sym,"").replace(/,\s*,/g,",").replace(/^,\s*|,\s*$/g,"").trim();
      chip.classList.remove("active");
    } else {
      ta.value = curr ? `${curr}, ${sym}` : sym;
      chip.classList.add("active");
    }
  });
});

// ── Loader animation ───────────────────────────────────────────────────────
let loaderTimer = null;
function startLoader() {
  const steps = ["ls1","ls2","ls3","ls4"];
  let i = 0;
  document.getElementById("loadingOverlay").style.display = "flex";
  steps.forEach(s => document.getElementById(s)?.classList.remove("active"));
  document.getElementById(steps[0])?.classList.add("active");
  loaderTimer = setInterval(() => {
    if (i < steps.length - 1) {
      i++;
      steps.forEach(s => document.getElementById(s)?.classList.remove("active"));
      document.getElementById(steps[i])?.classList.add("active");
    }
  }, 600);
}
function stopLoader() {
  clearInterval(loaderTimer);
  document.getElementById("loadingOverlay").style.display = "none";
}

// ── Main function ──────────────────────────────────────────────────────────
async function analyseSymptoms() {
  const symptoms = document.getElementById("symptoms").value.trim();
  const city     = document.getElementById("city").value.trim();
  const budget   = parseInt(document.getElementById("budget").value) || 0;

  if (!symptoms) { alert("⚠️ Please describe your symptoms."); return; }
  if (!city)     { alert("⚠️ Please select your city."); return; }
  if (!budget)   { alert("⚠️ Please enter your budget (₹)."); return; }

  startLoader();
  document.getElementById("results").style.display = "none";

  try {
    const resp = await fetch("/analyse", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symptoms, city, budget })
    });
    const data = await resp.json();
    if (data.error) { alert("Error: " + data.error); return; }

    renderResults(data, city, budget);
    document.getElementById("results").style.display = "block";

    // Auto-inject chatbot summary
    setTimeout(() => {
      const cname = data.condition ? data.condition.name : "general symptoms";
      const conf  = data.confidence ? ` (Confidence: ${data.confidence})` : "";
      appendMessage("bot",
        `✅ Analysis complete!\n\n` +
        `**Possible match:** ${cname}${conf}\n` +
        `**Severity:** ${data.severity?.toUpperCase()}\n` +
        `**Suggested pathway:** ${CARE_LABELS[data.care_type] || data.care_type}\n\n` +
        `Ask me: "explain my result", "what are my alternatives?", or "what if symptoms worsen?"`
      );
    }, 400);

    setTimeout(() => document.getElementById("results").scrollIntoView({ behavior:"smooth", block:"start" }), 120);
  } catch(err) {
    alert("Something went wrong. Please check your connection and try again.\n" + err.message);
  } finally {
    stopLoader();
  }
}

// ── Master render ──────────────────────────────────────────────────────────
function renderResults(d, city, budget) {
  renderEmergency(d.is_emergency, d.emergency);
  renderSeverityBanner(d.severity, d.condition, d.confidence);
  renderDecisionCard(d.care_type, d.recommendation, d.explanation, d.human_advice, d.risk_insight, d.is_emergency);
  renderCostBreakdown(d.cost_breakdown);
  renderCostComparison(d.cost_comparison, budget);
  renderHospitals(d.hospitals, d.care_type, city);
  renderAlternatives(d.alternatives, d.severity);
  renderSymptoms(d.matched_symptoms);
}

// ── Emergency ─────────────────────────────────────────────────────────────
function renderEmergency(isEmergency, emergency) {
  const el = document.getElementById("emergencyAlert");
  if (isEmergency && emergency) {
    el.style.display = "flex";
    document.getElementById("emergencyText").textContent = emergency.message;
  } else {
    el.style.display = "none";
  }
}

// ── Severity banner ────────────────────────────────────────────────────────
function renderSeverityBanner(severity, condition, confidence) {
  const ICONS  = { low:"✅", medium:"⚠️", critical:"🚨" };
  const NOTES  = {
    low:      "Manageable — basic care is a reasonable first step.",
    medium:   "Timely attention suggested — see a doctor within 24 hours.",
    critical: "Urgent care strongly suggested — do not delay.",
  };
  const b = document.getElementById("severityBanner");
  b.className = `severity-banner sev-${severity}`;
  document.getElementById("sevIcon").textContent  = ICONS[severity] || "ℹ️";
  document.getElementById("sevValue").textContent = severity.charAt(0).toUpperCase() + severity.slice(1) + " Severity";
  document.getElementById("sevNote").textContent  = NOTES[severity] || "";

  const cname    = condition ? condition.name : "General Concern";
  const confText = confidence ? `<span class="conf-pill">Confidence: ${confidence}</span>` : "";
  document.getElementById("cmbName").textContent  = cname;
  document.getElementById("cmbConf").innerHTML    = confText;
}

// ── Decision card ──────────────────────────────────────────────────────────
function renderDecisionCard(careType, recommendation, explanation, humanAdvice, riskInsight, isEmergency) {
  const btype = isEmergency ? "emergency" : careType;
  const badge = document.getElementById("recBadge");
  badge.className   = `rec-badge badge-${btype}`;
  badge.textContent = isEmergency ? "🚨 Emergency Care" : `${CARE_ICONS[careType]||""} ${CARE_LABELS[careType]||careType}`;

  document.getElementById("recText").textContent       = recommendation;
  document.getElementById("explanationText").textContent = explanation;

  if (humanAdvice) {
    document.getElementById("humanAdviceText").textContent = humanAdvice;
    document.getElementById("humanAdviceBox").style.display = "flex";
  } else {
    document.getElementById("humanAdviceBox").style.display = "none";
  }

  if (riskInsight) {
    document.getElementById("riskInsightText").textContent = riskInsight;
    document.getElementById("riskInsightBox").style.display = "block";
  } else {
    document.getElementById("riskInsightBox").style.display = "none";
  }
}

// ── Cost breakdown ─────────────────────────────────────────────────────────
function renderCostBreakdown(breakdown) {
  const el = document.getElementById("costBreakdownContent");
  if (!breakdown || !breakdown.items || breakdown.items.length === 0) {
    el.innerHTML = `<p class="no-breakdown">Itemised breakdown not available for this care type.</p>`;
    return;
  }
  const label = CARE_LABELS[breakdown.care_type] || breakdown.care_type;
  let html = `
    <div class="breakdown-header">
      <span class="breakdown-care-label">${CARE_ICONS[breakdown.care_type]||""} ${label}</span>
      <span style="font-size:.82rem;color:var(--text-sub);">Estimated range: ₹${breakdown.range_min?.toLocaleString("en-IN")} – ₹${breakdown.range_max?.toLocaleString("en-IN")}</span>
    </div>
    <div class="breakdown-items">`;
  breakdown.items.forEach(item => {
    html += `<div class="bd-row"><span class="bd-label">${item.label}</span><span class="bd-amount">₹${item.amount.toLocaleString("en-IN")}</span></div>`;
  });
  html += `</div>
    <div class="bd-total">
      <span class="bd-total-label">Estimated Total</span>
      <span class="bd-total-amount">₹${breakdown.estimated?.toLocaleString("en-IN")}</span>
    </div>`;
  el.innerHTML = html;
}

// ── Cost comparison ────────────────────────────────────────────────────────
function renderCostComparison(costComparison, budget) {
  const el = document.getElementById("costCompTable");
  if (!costComparison || costComparison.length === 0) {
    el.innerHTML = `<p class="no-breakdown">Cost data not available for this condition.</p>`;
    return;
  }
  let html = `<div class="cct-header"><div>Care Type</div><div>Min Cost</div><div>Max Cost</div><div>Covers</div><div>Budget Status</div></div>`;
  costComparison.forEach(row => {
    const recClass = row.is_recommended ? "row-recommended" : "";
    const vClass   = row.affordable ? "affordable" : "unaffordable";
    const verdict  = row.affordable ? "✅ Within budget" : `❌ Exceeds by ₹${row.shortfall?.toLocaleString("en-IN")}`;
    const badge    = row.is_recommended ? '<span class="cct-badge">✓ Suggested</span>' : "";
    html += `<div class="cct-row ${recClass}">
      <div class="cct-care">${CARE_ICONS[row.care_type]||""} ${row.label}${badge}</div>
      <div class="cct-range">₹${row.min?.toLocaleString("en-IN")}</div>
      <div class="cct-range">₹${row.max?.toLocaleString("en-IN")}</div>
      <div style="font-size:.76rem;color:var(--text-sub)">${row.includes}</div>
      <div class="cct-verdict ${vClass}">${verdict}</div>
    </div>`;
  });
  el.innerHTML = html;
  document.getElementById("budgetNote").textContent =
    `Your budget: ₹${budget.toLocaleString("en-IN")} · ✅ = within budget · ❌ = additional funds needed`;
}

// ── Hospitals (Top 3 ranked) ───────────────────────────────────────────────
function renderHospitals(hospitals, careType, city) {
  const el    = document.getElementById("hospitalsList");
  const noEl  = document.getElementById("noHospitals");
  const intro = document.getElementById("hospitalIntro");
  el.innerHTML = "";

  if (!hospitals || hospitals.length === 0) {
    noEl.style.display = "block";
    intro.textContent  = "";
    return;
  }
  noEl.style.display = "none";
  intro.textContent = `Showing top ${hospitals.length} suggestion${hospitals.length>1?"s":""} for ${city.charAt(0).toUpperCase()+city.slice(1)}, ranked by affordability, rating, and suitability.`;

  hospitals.forEach((h, i) => {
    const card = document.createElement("div");
    card.className = `hospital-card${i===0?" rank-1":""}`;
    const rankClass = RANK_CLASSES[i] || "";
    const rankSym   = RANK_SYMBOLS[i] || (i+1);
    const stars     = h.rating ? "⭐".repeat(Math.round(h.rating)) : "";
    card.innerHTML = `
      <div class="hosp-rank ${rankClass}">${rankSym}</div>
      <div class="hosp-name">${h.name}</div>
      <div class="hosp-meta">
        <span class="hosp-type ${h.type}">${h.type.toUpperCase()}</span>
        <span class="hosp-rating">${h.rating ? `⭐ ${h.rating}` : ""}</span>
        <span class="hosp-distance">📍 ~${h.distance_km || "?"} km</span>
      </div>
      ${h.strength ? `<div class="hosp-strength">✦ ${h.strength}</div>` : ""}
      <div class="hosp-address">${h.address || city}</div>
      ${h.phone ? `<div class="hosp-phone">📞 ${h.phone}</div>` : ""}
      ${h.emergency ? `<div class="hosp-emergency">🚑 24/7 Emergency Available</div>` : ""}
      ${h.recommendation_reason ? `<div class="hosp-reason">🔍 ${h.recommendation_reason}</div>` : ""}
    `;
    el.appendChild(card);
  });
}

// ── Alternatives ───────────────────────────────────────────────────────────
function renderAlternatives(alternatives, severity) {
  const card  = document.getElementById("altCard");
  const grid  = document.getElementById("alternativesGrid");
  const intro = document.getElementById("altIntro");
  if (!alternatives || alternatives.length === 0) { card.style.display="none"; return; }
  card.style.display = "block";
  intro.textContent  = severity === "low"
    ? "Since severity is low, here are additional care options to consider:"
    : "If the primary suggestion doesn't work for you, here are alternatives:";
  grid.innerHTML = "";
  alternatives.forEach(alt => {
    const isDelayed  = alt.care_type === "delayed";
    const affordable = alt.affordable;
    const cardClass  = isDelayed ? "alt-delayed" : (affordable ? "alt-affordable" : "alt-unaffordable");
    const tagClass   = affordable ? "tag-yes" : "tag-no";
    const tagText    = affordable ? "✅ Affordable" : `⚠️ Need ₹${(alt.shortfall||0).toLocaleString("en-IN")} more`;
    const d = document.createElement("div");
    d.className = `alt-card ${cardClass}`;
    d.innerHTML = `
      <div class="alt-label">${alt.label}</div>
      <span class="alt-afford-tag ${tagClass}">${tagText}</span>
      <div class="alt-reason">${alt.reason}</div>
      ${alt.min !== undefined && !isDelayed
        ? `<div class="alt-cost">Cost: ₹${alt.min.toLocaleString("en-IN")} – ₹${alt.max.toLocaleString("en-IN")}</div>` : ""}
    `;
    grid.appendChild(d);
  });
}

// ── Matched symptoms ───────────────────────────────────────────────────────
function renderSymptoms(matched) {
  const el = document.getElementById("matchedSymptoms");
  el.innerHTML = "";
  if (matched && matched.length > 0) {
    matched.forEach(s => {
      const t = document.createElement("span");
      t.className = `stag ${s.severity}`;
      t.textContent = `${s.name.replace(/_/g," ")} (${s.severity})`;
      el.appendChild(t);
    });
  } else {
    el.innerHTML = `<span class="no-symptoms">No specific symptoms matched — general guidance applied.</span>`;
  }
}

// ── Chatbot ────────────────────────────────────────────────────────────────
async function sendChat() {
  const input   = document.getElementById("chatInput");
  const message = input.value.trim();
  if (!message) return;
  appendMessage("user", message);
  input.value = "";
  const tid = appendMessage("bot", "…", "typing-msg");
  try {
    const resp = await fetch("/chat", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({ message })
    });
    const data = await resp.json();
    document.getElementById(tid)?.remove();
    appendMessage("bot", data.reply || "Sorry, I couldn't process that.");
  } catch(err) {
    document.getElementById(tid)?.remove();
    appendMessage("bot", "Connection error. Please try again.");
  }
}

function appendMessage(type, text, extraId="") {
  const container = document.getElementById("chatMessages");
  const div = document.createElement("div");
  const id  = extraId || `msg-${Date.now()}`;
  div.id = id; div.className = `chat-msg ${type}-msg`;
  const fmt = String(text)
    .replace(/\n/g,"<br/>")
    .replace(/\*\*(.*?)\*\*/g,"<strong>$1</strong>");
  if (type === "bot") {
    div.innerHTML = `<div class="bot-avatar">⚕</div><div class="msg-bubble">${fmt}</div>`;
  } else {
    div.innerHTML = `<div class="msg-bubble">${fmt}</div>`;
  }
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return id;
}

function quickChat(text) {
  document.getElementById("chatInput").value = text;
  sendChat();
}
