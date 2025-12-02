import re
import math
import pandas as pd
import streamlit as st
import plotly.express as px

# Imports from your modules
from modules.risk_profile import calculate_risk_profile
from modules.goals import Goal, describe_goal_plan

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="Robo Advisor",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. CUSTOM CSS (Rocket Theme + Screenshot Styles)
def apply_custom_styling():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
            
            /* GLOBAL THEME */
            html, body, [class*="css"] {
                font-family: 'Poppins', sans-serif;
                background-color: #050A18;
                color: #ffffff;
            }
            
            /* HIDE DEFAULTS */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            
            /* BACKGROUND */
            .stApp {
                background: #050A18;
                background-image: 
                    linear-gradient(120deg, rgba(255, 0, 122, 0.15) 0%, rgba(108, 40, 254, 0.15) 50%, rgba(0, 240, 255, 0.15) 100%);
                background-attachment: fixed;
            }

            /* TEXT */
            h1, h2, h3, h4 { color: white !important; font-weight: 700 !important; }
            p, label, li, span { color: #cbd5e1 !important; }
            
            .gradient-text {
                background: -webkit-linear-gradient(0deg, #00F0FF, #6C28FE);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-weight: 800;
            }
            .big-hero-text {
                font-size: 3.5rem !important;
                line-height: 1.2 !important;
                margin-bottom: 20px;
            }

            /* INPUTS */
            .stTextInput > div > div > input, 
            .stNumberInput > div > div > input, 
            .stSelectbox > div > div > div {
                background-color: rgba(30, 41, 59, 0.8) !important;
                color: white !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                border-radius: 12px !important;
            }

            /* BUTTONS */
            .stButton > button {
                background: linear-gradient(90deg, #6C28FE, #FF007A);
                color: white;
                border: none;
                border-radius: 50px;
                padding: 0.5rem 1.5rem;
                font-weight: 600;
                transition: transform 0.2s;
            }
            .stButton > button:hover {
                transform: scale(1.05);
                box-shadow: 0 0 15px rgba(108, 40, 254, 0.5);
                color: white !important;
            }

            /* CARDS */
            .card-like {
                background-color: rgba(17, 24, 39, 0.6);
                padding: 1.5rem;
                border-radius: 1rem;
                border: 1px solid rgba(255,255,255,0.08);
                margin-bottom: 1rem;
                backdrop-filter: blur(10px);
            }

            /* METRICS */
            [data-testid="stMetricValue"] {
                font-size: 2.5rem !important;
                background: -webkit-linear-gradient(0deg, #ffffff, #cbd5e1);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            /* PILLS (For Goals/Risk) */
            .pill {
                display: inline-block; padding: 0.2rem 0.8rem; border-radius: 999px;
                font-size: 0.75rem; font-weight: 600; color: white !important;
            }
            .pill-green { background-color: rgba(34, 197, 94, 0.2); border: 1px solid rgba(34, 197, 94, 0.5); }
            .pill-yellow { background-color: rgba(251, 191, 36, 0.2); border: 1px solid rgba(251, 191, 36, 0.5); }
            .pill-red { background-color: rgba(239, 68, 68, 0.2); border: 1px solid rgba(239, 68, 68, 0.5); }
        </style>
    """, unsafe_allow_html=True)

apply_custom_styling()

ROCKET_SVG = """
<div style="animation: float 6s ease-in-out infinite;">
    <svg viewBox="0 0 512 512" width="100%" height="auto" fill="none" xmlns="http://www.w3.org/2000/svg" style="max-width: 500px; filter: drop-shadow(0 20px 50px rgba(108,40,254,0.5));">
        <path d="M256 48C256 48 368 144 368 272C368 360 320 448 256 448C192 448 144 360 144 272C144 144 256 48 256 48Z" fill="url(#bodyGrad)"/>
        <circle cx="256" cy="220" r="40" fill="#1F2937" stroke="#6C28FE" stroke-width="8"/>
        <circle cx="256" cy="220" r="30" fill="#00F0FF" opacity="0.3"/>
        <path d="M144 272C100 300 80 360 80 400C110 400 160 380 192 360" fill="#3B82F6"/>
        <path d="M368 272C412 300 432 360 432 400C402 400 352 380 320 360" fill="#3B82F6"/>
        <path d="M256 448L230 480C230 480 240 512 256 512C272 512 282 480 282 480L256 448Z" fill="#F472B6"/>
        <defs>
            <linearGradient id="bodyGrad" x1="256" y1="48" x2="256" y2="448" gradientUnits="userSpaceOnUse">
                <stop stop-color="#F3F4F6"/>
                <stop offset="0.5" stop-color="#93C5FD"/>
                <stop offset="1" stop-color="#3B82F6"/>
            </linearGradient>
        </defs>
        <style>
            @keyframes float {
                0% { transform: translateY(0px); }
                50% { transform: translateY(-20px); }
                100% { transform: translateY(0px); }
            }
        </style>
    </svg>
</div>
"""

# 3. STATE MANAGEMENT
if "messages" not in st.session_state: st.session_state.messages = []
if "risk_profile" not in st.session_state: st.session_state.risk_profile = None
if "goals" not in st.session_state: st.session_state.goals = []
if "last_plan" not in st.session_state: st.session_state.last_plan = None
if "last_plan_saved" not in st.session_state: st.session_state.last_plan_saved = True
if "current_page" not in st.session_state: st.session_state.current_page = "home"
if "show_risk_panel" not in st.session_state: st.session_state.show_risk_panel = False
if "prefill_text" not in st.session_state: st.session_state.prefill_text = ""

# Risk Defaults (Full set from original)
if "age" not in st.session_state: st.session_state.age = 25
if "income_stability" not in st.session_state: st.session_state.income_stability = 3
if "horizon_years" not in st.session_state: st.session_state.horizon_years = 10
if "crash_reaction" not in st.session_state: st.session_state.crash_reaction = 3
if "experience" not in st.session_state: st.session_state.experience = 2
if "dip_behavior" not in st.session_state: st.session_state.dip_behavior = 3
if "inflation" not in st.session_state: st.session_state.inflation = 5.0
if "monthly_income" not in st.session_state: st.session_state.monthly_income = 50000.0
if "goal_type" not in st.session_state: st.session_state.goal_type = "General"

# 4. META & HELPER LOGIC
GOAL_TYPES = {
    "General": {"icon": "📌", "note": "Flexible goal.", "default_return": 12.0, "amount_hint": "2L, 5L, 10L"},
    "Education": {"icon": "🎓", "note": "Equity-heavy.", "default_return": 11.0, "amount_hint": "15L - 30L"},
    "House": {"icon": "🏠", "note": "Medium/Long term.", "default_return": 10.0, "amount_hint": "40L - 1.5Cr"},
    "Marriage": {"icon": "💍", "note": "5-15 years.", "default_return": 11.0, "amount_hint": "10L - 25L"},
    "Vehicle": {"icon": "🚗", "note": "Shorter term.", "default_return": 9.0, "amount_hint": "8L - 15L"},
    "Retirement": {"icon": "🧓", "note": "Long term.", "default_return": 12.0, "amount_hint": "1Cr - 3Cr"},
}

def extract_goal_details(text: str):
    text = text.lower()
    amount = None
    m_amt = re.search(r"(\d+)\s*(l|lac|lakh|crore|cr|k|rs|₹)", text)
    if m_amt:
        n = float(m_amt.group(1))
        unit = m_amt.group(2)
        if unit in ("l", "lac", "lakh"): amount = n * 1_00_000
        elif unit in ("cr", "crore"): amount = n * 1_00_00_000
        elif unit == "k": amount = n * 1_000
        else: amount = n
    years = None
    m_years = re.search(r"(\d+)\s*(year|years|yr|yrs)", text)
    if m_years: years = int(m_years.group(1))
    expected_return = None
    m_ret = re.search(r"(\d+(\.\d+)?)\s*%", text)
    if m_ret: expected_return = float(m_ret.group(1))
    return amount, years, expected_return

def calculate_sip(target_amount, years, annual_return):
    r = annual_return / 100.0
    monthly_rate = r / 12.0
    months = years * 12
    if monthly_rate == 0: return target_amount / months
    sip = target_amount * monthly_rate / ((1 + monthly_rate) ** months - 1)
    return sip

def sip_growth_schedule(monthly_sip, years, annual_return):
    r = annual_return / 100.0
    monthly_rate = r / 12.0
    values = []
    for yr in range(1, years + 1):
        m = yr * 12
        if monthly_rate == 0: fv = monthly_sip * m
        else: fv = monthly_sip * ((1 + monthly_rate) ** m - 1) / monthly_rate
        values.append((yr, fv))
    return values

def get_allocation_for_profile(profile: str):
    if not profile: profile = "Moderate"
    p = profile.lower()
    if "aggress" in p: return {"Equity Funds": 70, "Hybrid / Balanced": 20, "Debt / Liquid": 10}
    if "conserv" in p: return {"Equity Funds": 20, "Hybrid / Balanced": 30, "Debt / Liquid": 50}
    return {"Equity Funds": 50, "Hybrid / Balanced": 30, "Debt / Liquid": 20}

def risk_heat_label(risk_profile: str, years: int):
    rp = (risk_profile or "Moderate").lower()
    if years <= 5: horizon_factor = "short"
    elif years <= 12: horizon_factor = "medium"
    else: horizon_factor = "long"
    if "aggress" in rp and horizon_factor == "short": return "🔥 High execution risk", "High return expectations over a short horizon. Consider more debt / hybrid."
    if "conserv" in rp and horizon_factor == "long": return "🟡 Cautious but slow", "Very conservative profile for a long-term goal. You may fall short if SIP is too low."
    if horizon_factor == "short": return "🟠 Medium–High risk", "Short horizon means limited time to recover from volatility."
    if horizon_factor == "long": return "🟢 Comfortable zone", "Long horizon gives you time to ride out market volatility."
    return "🟡 Balanced risk", "Overall risk and horizon look reasonably aligned."

def affordability_comment(monthly_sip: float, monthly_income: float):
    if monthly_income <= 0: return "ℹ️ Add income in Budget Planner to see hints."
    ratio = monthly_sip / monthly_income
    if ratio > 0.5: return "🔴 This SIP is > 50% of your income. It may not be affordable."
    if ratio > 0.3: return "🟠 This SIP is 30–50% of your income. A bit tight."
    if ratio > 0.15: return "🟡 This SIP is moderate (15–30% of income)."
    return "🟢 This SIP is under 15% of your income. Affordable."

def generate_insights(lp):
    insights = []
    years = lp["years"]
    ret = lp["return"]
    infl = lp["inflation"]
    if years < 5 and ret >= 12: insights.append("For <5 years, assuming 12%+ returns is aggressive.")
    if years >= 10 and ret <= 9: insights.append("For 10+ years, consider higher equity allocation to beat inflation.")
    if infl < 4: insights.append("Inflation assumption is low. 5-7% is standard.")
    if infl > 7: insights.append("High inflation assumption keeps you safe.")
    if not insights: insights.append("Assumptions look broadly reasonable.")
    return insights

def get_investment_suggestions(profile: str, goal_type: str, years: int):
    profile = (profile or "Moderate").lower()
    goal_type = (goal_type or "General").lower()
    horizon = "short" if years <= 5 else "medium" if years <= 10 else "long"
    suggestions = []
    if horizon == "short":
        suggestions.append({"title": "Debt / Liquid mutual funds", "desc": "Focus on capital protection for goals under 5 years."})
        suggestions.append({"title": "High-interest RD / FD", "desc": "Predictable, low-risk returns."})
    elif horizon == "medium":
        suggestions.append({"title": "Hybrid / Balanced Advantage", "desc": "Blends equity and debt, adjusting automatically."})
        if "aggress" in profile or "moderate" in profile: suggestions.append({"title": "Large-cap index funds", "desc": "Growth with lower volatility than mid-caps."})
    else: # long
        suggestions.append({"title": "Equity index funds", "desc": "Low-cost broad market growth for 10+ years."})
        suggestions.append({"title": "Flexi-cap funds", "desc": "Active management across market caps."})
        if "conserv" in profile: suggestions.append({"title": "Hybrid equity-oriented", "desc": "Equity potential with debt cushioning."})
    if "house" in goal_type: suggestions.append({"title": "Dedicated House Portfolio", "desc": "Keep separate to avoid dipping."})
    if "education" in goal_type: suggestions.append({"title": "Inflation-focused", "desc": "Edu inflation is often higher than CPI."})
    return suggestions

def get_detailed_investment_split(profile: str, years: int):
    profile = (profile or "Moderate").lower()
    horizon = "short" if years <= 5 else "medium" if years <= 10 else "long"
    split = []
    if "aggress" in profile:
        if horizon == "long": split = [{"Bucket": "Core Equity", "Percent": 45}, {"Bucket": "Mid/Small Cap", "Percent": 20}, {"Bucket": "Thematic", "Percent": 10}, {"Bucket": "Hybrid", "Percent": 15}, {"Bucket": "Debt", "Percent": 10}]
        elif horizon == "medium": split = [{"Bucket": "Core Equity", "Percent": 35}, {"Bucket": "Mid Cap", "Percent": 15}, {"Bucket": "Hybrid", "Percent": 25}, {"Bucket": "Debt", "Percent": 25}]
        else: split = [{"Bucket": "Large Cap", "Percent": 25}, {"Bucket": "Hybrid", "Percent": 25}, {"Bucket": "Debt", "Percent": 30}, {"Bucket": "Cash", "Percent": 20}]
    elif "conserv" in profile:
        if horizon == "long": split = [{"Bucket": "Large Cap", "Percent": 30}, {"Bucket": "Hybrid", "Percent": 30}, {"Bucket": "Debt", "Percent": 30}, {"Bucket": "Cash", "Percent": 10}]
        elif horizon == "medium": split = [{"Bucket": "Large Cap", "Percent": 25}, {"Bucket": "Hybrid", "Percent": 30}, {"Bucket": "Debt", "Percent": 35}, {"Bucket": "Cash", "Percent": 10}]
        else: split = [{"Bucket": "Debt", "Percent": 50}, {"Bucket": "Cash", "Percent": 30}, {"Bucket": "Hybrid", "Percent": 20}]
    else: # moderate
        if horizon == "long": split = [{"Bucket": "Core Equity", "Percent": 40}, {"Bucket": "Mid Cap", "Percent": 15}, {"Bucket": "Hybrid", "Percent": 20}, {"Bucket": "Debt", "Percent": 15}, {"Bucket": "Cash", "Percent": 10}]
        elif horizon == "medium": split = [{"Bucket": "Core Equity", "Percent": 30}, {"Bucket": "Hybrid", "Percent": 30}, {"Bucket": "Debt", "Percent": 30}, {"Bucket": "Cash", "Percent": 10}]
        else: split = [{"Bucket": "Debt", "Percent": 45}, {"Bucket": "Cash", "Percent": 25}, {"Bucket": "Hybrid", "Percent": 30}]
    return split

# ---------- GLOBAL NAVIGATION ----------
c1, c2, c3, c4, c5 = st.columns([0.4, 0.15, 0.15, 0.15, 0.15])
with c1: st.markdown("### 🚀 Robo<span class='gradient-text'>Advisor</span>", unsafe_allow_html=True)
with c2: 
    if st.button("Home", use_container_width=True): st.session_state.current_page = "home"; st.rerun()
with c3: 
    if st.button("Planner", use_container_width=True): st.session_state.current_page = "chat"; st.rerun()
with c4: 
    if st.button("Budget", use_container_width=True): st.session_state.current_page = "budget"; st.rerun()
with c5: 
    if st.button("Analytics", use_container_width=True): st.session_state.current_page = "analytics"; st.rerun()
st.markdown("<br>", unsafe_allow_html=True)

page = st.session_state.current_page

# === HOME PAGE ===
if page == "home":
    col_text, col_img = st.columns([1, 1], gap="large")
    with col_text:
        st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
        st.markdown("<h1 class='big-hero-text'>Boost Your <br><span class='gradient-text'>Future Wealth</span></h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 1.2rem; opacity: 0.8;'>Smart, risk-aware financial planning powered by algorithms.</p>", unsafe_allow_html=True)
        c_h1, c_h2 = st.columns(2)
        with c_h1:
            if st.button("Start Planning ➝", use_container_width=True): st.session_state.current_page = "chat"; st.rerun()
        with c_h2:
            if st.button("Check Budget ➝", use_container_width=True): st.session_state.current_page = "budget"; st.rerun()
        st.markdown("<br><div class='card-like'><p> Create Your Plans Now &nbsp;&nbsp;</p></div>", unsafe_allow_html=True)
    with col_img: st.markdown(ROCKET_SVG, unsafe_allow_html=True)

# === CHAT / PLANNER PAGE (EXACT ORIGINAL LOGIC RESTORED) ===
elif page == "chat":
    # Top nav logic from original (Nav is already global, but this matches local logic)
    nav_left, nav_center, nav_right = st.columns([1, 1, 1])
    with nav_left:
        if st.button("← Home", use_container_width=True): st.session_state.current_page = "home"; st.rerun()
    with nav_center:
        if st.button("Budget Planner", use_container_width=True): st.session_state.current_page = "budget"; st.rerun()
    with nav_right:
        if st.button("Analytics →", use_container_width=True): st.session_state.current_page = "analytics"; st.rerun()

    st.markdown("---")

    # Risk & Assumptions Toggle + Goal Type (Original Layout)
    top_row = st.columns([2, 3, 3])
    with top_row[0]:
        if st.button("⚙️ Risk & assumptions", use_container_width=True):
            st.session_state.show_risk_panel = not st.session_state.show_risk_panel
            st.rerun()

    with top_row[1]:
        st.session_state.goal_type = st.selectbox(
            "Goal type",
            list(GOAL_TYPES.keys()),
            index=list(GOAL_TYPES.keys()).index(st.session_state.goal_type),
        )
    with top_row[2]:
        gt_meta = GOAL_TYPES[st.session_state.goal_type]
        st.markdown(
            f"**{gt_meta['icon']} {st.session_state.goal_type} goal** \n"
            f"{gt_meta['note']}"
        )

    # Risk Panel (Original Layout - Expandable below)
    if st.session_state.show_risk_panel:
        st.markdown("#### ⚙️ Configure risk profile & assumptions")
        with st.container():
            c1, c2, c3 = st.columns(3)
            with c1:
                st.session_state.age = st.number_input("Age", 18, 80, value=st.session_state.age, step=1)
                st.session_state.income_stability = st.slider("Income stability (1–5)", 1, 5, st.session_state.income_stability)
                st.session_state.horizon_years = st.slider("Typical investment horizon (years)", 1, 40, st.session_state.horizon_years)
            with c2:
                st.session_state.crash_reaction = st.slider("Reaction to crashes (1–5)", 1, 5, st.session_state.crash_reaction)
                st.session_state.experience = st.slider("Investment experience (1–5)", 1, 5, st.session_state.experience)
                st.session_state.dip_behavior = st.slider("If portfolio drops 10% (1=sell, 5=buy more)", 1, 5, st.session_state.dip_behavior)
            with c3:
                st.session_state.inflation = st.slider("Expected inflation (%)", 0.0, 10.0, st.session_state.inflation, step=0.5)
                st.session_state.monthly_income = st.number_input("Approx. monthly income (₹)", min_value=0.0, value=st.session_state.monthly_income, step=5000.0)

                if st.button("Update risk profile", use_container_width=True):
                    age_score = 5 if st.session_state.age < 30 else 3 if st.session_state.age < 50 else 1
                    answers = [age_score, st.session_state.income_stability, st.session_state.horizon_years / 5,
                               st.session_state.crash_reaction, st.session_state.experience, st.session_state.dip_behavior]
                    profile = calculate_risk_profile(answers)
                    st.session_state.risk_profile = profile
                    st.success(f"Risk profile updated: **{profile}**")

        st.caption("These settings influence how your plans and suggestions are interpreted.")

    st.markdown("---")
    st.subheader("💬 Chat with your robo-advisor")
    st.caption("Describe your financial goal in natural language. I'll use your goal type, risk profile & inflation settings.")

    # Quick Examples (Original Layout)
    qc1, qc2, qc3 = st.columns(3)
    with qc1:
        if st.button("💻 1L in 3 yrs"): st.session_state.prefill_text = "Plan a SIP for 1 lakh in 3 years"
    with qc2:
        if st.button("🏠 50L in 15 yrs"): st.session_state.prefill_text = "Plan a SIP for 50 lakh in 15 years"
    with qc3:
        if st.button("🎓 20L in 10 yrs @ 12%"): st.session_state.prefill_text = "Plan a SIP for 20 lakh in 10 years at 12%"

    # Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input
    user_input = st.chat_input("Describe your goal (e.g., 'Plan a SIP for 20 lakh in 10 years at 12%')")

    if st.session_state.prefill_text and not user_input:
        user_input = st.session_state.prefill_text
        st.session_state.prefill_text = ""

    # --- CORE CHAT LOGIC REVERTED EXACTLY ---
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Logic
        rp = st.session_state.risk_profile or "Moderate"
        lower = user_input.lower()
        amount, years, expected_return = extract_goal_details(lower)
        goal_type = st.session_state.goal_type
        gt_meta_local = GOAL_TYPES[goal_type]

        # CASE A: Missing info
        if amount is None or years is None:
            parts = []
            parts.append(f"{gt_meta_local['icon']} **{goal_type} goal** – let's make this more specific.")
            if years is None:
                parts.append("I couldn't see a clear **time horizon**. Tell me roughly how many years (e.g., `in 10 years`).")
            else:
                parts.append(f"I can see you have about **{years} years** for this goal.")
            if amount is None:
                parts.append("I also need an approximate **target amount in today's value**. Just a ballpark.")
            parts.append(f"For a **{goal_type.lower()}** goal, typical ranges: {gt_meta_local['amount_hint']}")
            parts.append("You can say things like:\n- `Plan for 60 lakh in 10 years`")
            reply = "\n\n".join(parts)
        
        # CASE B: Full plan
        else:
            assumed_return = expected_return if expected_return is not None else gt_meta_local["default_return"]
            infl = st.session_state.inflation
            inflated_target = amount * ((1 + infl / 100.0) ** years)
            monthly_sip = calculate_sip(inflated_target, years, assumed_return)

            goal = Goal(f"{goal_type} Goal (inflation-adjusted)", inflated_target, years, assumed_return, rp)
            plan_text = describe_goal_plan(goal)

            st.session_state.last_plan = {
                "original_target": amount, "inflated_target": inflated_target, "years": years,
                "inflation": infl, "return": assumed_return, "sip": monthly_sip, 
                "risk_profile": rp, "goal_type": goal_type
            }
            st.session_state.last_plan_saved = False

            reply = (
                f"{gt_meta_local['icon']} **{goal_type} goal**\n\n"
                f"Here's your customized plan based on your **{rp}** risk profile:\n\n"
                f"- Original target: **₹{amount:,.0f}** today\n"
                f"- Note: _{gt_meta_local['note']}_\n"
                f"- Inflation: **{infl:.1f}%** per year for **{years}** years\n"
                f"- Future target: **₹{inflated_target:,.0f}**\n"
                f"- Expected return: **{assumed_return:.1f}%** per year\n"
                f"- Estimated SIP: **₹{monthly_sip:,.0f}**\n\n"
                f"{plan_text}\n\n"
                "Note: Returns and inflation are assumptions; actual outcomes may differ."
            )

        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

    # Save Prompt
    if st.session_state.last_plan and not st.session_state.last_plan_saved:
        st.markdown("---")
        st.subheader("📌 Save this plan?")
        st.caption("Store this plan in your Dashboard for comparison.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, save this goal"):
                lp = st.session_state.last_plan
                st.session_state.goals.append({
                    "Goal": f"Goal {len(st.session_state.goals) + 1}",
                    "Goal type": lp.get("goal_type", "General"),
                    "Original Target (₹)": round(lp["original_target"]),
                    "Inflation-adjusted Target (₹)": round(lp["inflated_target"]),
                    "Years": lp["years"], "Risk": lp["risk_profile"],
                    "Inflation (%)": lp["inflation"], "Return (%)": lp["return"],
                    "Monthly SIP (₹)": round(lp["sip"]),
                })
                st.session_state.last_plan_saved = True
                st.success("Goal saved to your dashboard.")
        with col2:
            if st.button("❌ No, don't save this"):
                st.session_state.last_plan_saved = True
                st.info("Goal not saved.")

# === BUDGET PAGE ===
elif page == "budget":
    st.markdown("## 💰 Income & Budget")
    col_in, col_sum = st.columns([1, 1])
    with col_in:
        st.markdown("#### Monthly Inputs")
        income = st.number_input("Net Income (₹)", value=float(st.session_state.monthly_income), step=5000.0)
        st.session_state.monthly_income = income
        essential = st.number_input("Essential Expenses (₹)", value=25000.0, step=1000.0)
        lifestyle = st.number_input("Lifestyle Expenses (₹)", value=10000.0, step=1000.0)
        current_sip = st.number_input("Current SIP (₹)", value=5000.0, step=500.0)
        emergency_months = st.slider("Emergency Fund (Months)", 3, 12, 6)
        current_emergency = st.number_input("Current Emergency Savings (₹)", value=0.0)
        total_exp = essential + lifestyle
        free_cash = max(income - total_exp - current_sip, 0)
        savings_rate = (current_sip + free_cash) / income if income > 0 else 0
    with col_sum:
        st.markdown("#### Summary")
        c1, c2 = st.columns(2)
        c1.metric("Income", f"₹{income:,.0f}")
        c2.metric("Free Cash", f"₹{free_cash:,.0f}")
        habit_cls, habit_txt = "pill-green", "Good"
        if savings_rate < 0.1: habit_cls, habit_txt = "pill-red", "Low"
        elif savings_rate < 0.2: habit_cls, habit_txt = "pill-yellow", "Okay"
        st.markdown(f"<span class='pill {habit_cls}'>Habit: {habit_txt} ({savings_rate*100:.1f}%)</span>", unsafe_allow_html=True)
        df_pie = pd.DataFrame({"Category": ["Essentials", "Lifestyle", "Investments", "Free Cash"], "Amount": [essential, lifestyle, current_sip, free_cash]})
        fig = px.pie(df_pie, values="Amount", names="Category", hole=0.4, template="plotly_dark", color_discrete_sequence=['#3B82F6', '#F472B6', '#6C28FE', '#10B981'])
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")
    tab_em, tab_goalcheck, tab_deploy = st.tabs(["🛟 Emergency", "🎯 Goal Check", "🧭 Deployment"])
    with tab_em:
        req_emergency = total_exp * emergency_months
        gap = max(req_emergency - current_emergency, 0)
        c1, c2, c3 = st.columns(3)
        c1.metric("Required", f"₹{req_emergency:,.0f}")
        c2.metric("Current", f"₹{current_emergency:,.0f}")
        c3.metric("Gap", f"₹{gap:,.0f}", delta=-gap if gap>0 else "Done")
        if gap > 0: st.warning(f"Build emergency fund! You are short by ₹{gap:,.0f}")
        else: st.success("Emergency fund fully sorted!")
    with tab_goalcheck:
        if st.session_state.goals:
            df_g = pd.DataFrame(st.session_state.goals)
            req_sip = df_g["Monthly SIP (₹)"].sum()
            st.metric("Total Goal SIP Needed", f"₹{req_sip:,.0f}")
            if req_sip > (free_cash + current_sip): st.error("Shortfall! Your budget cannot support all goal SIPs.")
            else: st.success("On Track! Your budget covers your goals.")
        else: st.info("No goals saved yet.")
    with tab_deploy:
        st.markdown("#### Where to invest surplus?")
        if gap > 0: st.markdown("🚨 **Priority 1:** Fill Emergency Gap (Liquid Funds / FD).")
        else:
            st.markdown("✅ **Priority 1:** Maximize Goal SIPs.")
            suggestions = get_investment_suggestions(st.session_state.risk_profile, "General", 10)
            for s in suggestions[:2]: st.markdown(f"- **{s['title']}**: {s['desc']}")

# === ANALYTICS / DASHBOARD ===
elif page == "analytics":
    st.markdown("## 📊 Wealth Dashboard")
    tab_ov, tab_whatif, tab_alloc, tab_goals = st.tabs(["Overview", "What-if", "Allocation", "Saved Goals"])
    lp = st.session_state.last_plan
    with tab_ov:
        if lp:
            c1, c2, c3 = st.columns(3)
            c1.metric("Target", f"₹{lp['inflated_target']:,.0f}")
            c2.metric("SIP", f"₹{lp['sip']:,.0f}")
            c3.metric("Risk", lp['risk_profile'])
            insights = generate_insights(lp)
            st.markdown("#### Insights")
            for i in insights: st.markdown(f"- {i}")
            sched = sip_growth_schedule(lp['sip'], lp['years'], lp['return'])
            df_chart = pd.DataFrame(sched, columns=["Year", "Corpus"])
            st.line_chart(df_chart, x="Year", y="Corpus")
        else: st.info("Plan a goal to see overview.")
    with tab_whatif:
        if lp:
            st.markdown("#### Simulation")
            c1, c2 = st.columns(2)
            w_years = c1.slider("Years", 1, 40, lp['years'])
            w_return = c2.slider("Return %", 5.0, 20.0, lp['return'])
            w_sip = calculate_sip(lp['inflated_target'], w_years, w_return)
            st.metric("New SIP Required", f"₹{w_sip:,.0f}", delta=f"{lp['sip']-w_sip:,.0f} saved")
        else: st.info("Plan a goal to run simulations.")
    with tab_alloc:
        if lp:
            alloc = get_allocation_for_profile(lp['risk_profile'])
            detailed = get_detailed_investment_split(lp['risk_profile'], lp['years'])
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### Asset Class")
                fig = px.pie(values=list(alloc.values()), names=list(alloc.keys()), hole=0.4, template="plotly_dark")
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                st.markdown("#### Detailed Split")
                df_det = pd.DataFrame(detailed)
                fig2 = px.bar(df_det, x="Bucket", y="Percent", template="plotly_dark")
                fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig2, use_container_width=True)
        else: st.info("Plan a goal to see allocations.")
    with tab_goals:
        if st.session_state.goals:
            df = pd.DataFrame(st.session_state.goals)
            total_sip = df["Monthly SIP (₹)"].sum()
            total_future = df["Inflation-adjusted Target (₹)"].sum()
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Goals", len(df))
            c2.metric("Total Monthly SIP", f"₹{total_sip:,.0f}")
            c3.metric("Total Target Wealth", f"₹{total_future:,.0f}")
            st.markdown("---")
            st.markdown("#### 🗂 Your Goal Cards")
            for g in st.session_state.goals:
                icon = GOAL_TYPES.get(g["Goal type"], GOAL_TYPES["General"])["icon"]
                risk = (g["Risk"] or "Moderate").lower()
                pill_cls = "pill-red" if "aggress" in risk else "pill-green" if "conserv" in risk else "pill-yellow"
                st.markdown(f"""
<div class="card-like">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
        <div>
            <span style="font-size:1.4rem; margin-right:8px;">{icon}</span>
            <span style="font-size:1.1rem; font-weight:700;">{g['Goal']}</span>
            <span style="font-size:0.9rem; opacity:0.7; margin-left:8px;">({g['Goal type']})</span>
        </div>
        <span class="pill {pill_cls}">{g['Risk']}</span>
    </div>
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; font-size:0.95rem;">
        <div style="background:rgba(255,255,255,0.05); padding:10px; border-radius:8px;">
            <div style="font-size:0.8rem; color:#cbd5e1;">Target Amount</div>
            <div style="font-size:1.1rem; font-weight:600; color:#fff;">₹{g['Inflation-adjusted Target (₹)']:,.0f}</div>
            <div style="font-size:0.75rem; color:#94a3b8;">in {g['Years']} years</div>
        </div>
        <div style="background:rgba(255,255,255,0.05); padding:10px; border-radius:8px;">
            <div style="font-size:0.8rem; color:#cbd5e1;">Required SIP</div>
            <div style="font-size:1.1rem; font-weight:600; color:#00F0FF;">₹{g['Monthly SIP (₹)']:,.0f}</div>
            <div style="font-size:0.75rem; color:#94a3b8;">@ {g['Return (%)']:.1f}% return</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
        else: st.info("No saved goals. Use the Planner to create one.")