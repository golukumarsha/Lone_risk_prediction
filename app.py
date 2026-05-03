import streamlit as st
import joblib
import numpy as np
import warnings
import os
import pandas as pd
from database import init_db, save_prediction, get_all_predictions, get_stats

warnings.filterwarnings("ignore")

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Loan Approval Predictor",
    page_icon="🏦",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: white; }
    .title-text {
        font-size: 2.5rem; font-weight: 800; text-align: center;
        background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .subtitle-text { text-align: center; color: rgba(255,255,255,0.6); font-size: 1rem; margin-bottom: 2rem; }
    .section-header {
        font-size: 1.1rem; font-weight: 700; color: #a78bfa;
        border-left: 4px solid #a78bfa; padding-left: 10px; margin: 20px 0 10px 0;
    }
    .approved-banner {
        background: linear-gradient(135deg, #065f46, #10b981); border-radius: 16px;
        padding: 24px; text-align: center; border: 2px solid #34d399;
        box-shadow: 0 0 30px rgba(52,211,153,0.3);
    }
    .rejected-banner {
        background: linear-gradient(135deg, #7f1d1d, #ef4444); border-radius: 16px;
        padding: 24px; text-align: center; border: 2px solid #f87171;
        box-shadow: 0 0 30px rgba(239,68,68,0.3);
    }
    .result-icon { font-size: 3.5rem; }
    .result-title { font-size: 1.8rem; font-weight: 800; color: white; margin: 10px 0; }
    .result-sub { color: rgba(255,255,255,0.8); font-size: 0.95rem; }
    .prob-label { color: rgba(255,255,255,0.7); font-size: 0.85rem; margin-bottom: 4px; }
    section[data-testid="stSidebar"] {
        background: rgba(15,12,41,0.95); border-right: 1px solid rgba(255,255,255,0.1);
    }
    .stButton > button {
        width: 100%; background: linear-gradient(135deg, #7c3aed, #3b82f6);
        color: white; border: none; border-radius: 12px; padding: 14px;
        font-size: 1.1rem; font-weight: 700; cursor: pointer; transition: all 0.3s;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #6d28d9, #2563eb);
        transform: translateY(-2px); box-shadow: 0 8px 20px rgba(124,58,237,0.4);
    }
    label { color: rgba(255,255,255,0.85) !important; }
    .db-badge {
        background: rgba(52,211,153,0.15); border: 1px solid rgba(52,211,153,0.4);
        border-radius: 8px; padding: 6px 12px; font-size: 0.8rem;
        color: #34d399; display: inline-block; margin-top: 6px;
    }
</style>
""", unsafe_allow_html=True)


# ── Init DB & Load Model ───────────────────────────────────────────────────────
init_db()


@st.cache_resource
def load_model():
    return joblib.load("best_model_lone_prediction.pkl")


try:
    model = load_model()
    model_loaded = True
except Exception as e:
    model_loaded = False
    load_error = str(e)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏦 Loan Predictor")
    st.markdown("---")
    page = st.radio("📌 Navigate", ["🔍 Predict",
                    "📊 Dashboard", "📋 All Records"])
    st.markdown("---")
    st.markdown("**Model Info**")
    st.markdown(
        "- 🤖 KNN Classifier\n- 🔢 K = 7\n- 📊 31 Features\n- 🎯 Binary Class")
    st.markdown("---")
    stats = get_stats()
    st.markdown("**📈 Live Stats**")
    st.markdown(f"- Total: **{stats['total']}**")
    st.markdown(f"- ✅ Approved: **{stats['approved']}**")
    st.markdown(f"- ❌ Rejected: **{stats['rejected']}**")
    st.markdown("---")
    if model_loaded:
        st.success("✅ Model Ready")
    else:
        st.error("❌ Model Error")
    if os.environ.get("DATABASE_URL"):
        st.markdown(
            '<span class="db-badge">🗄️ PostgreSQL Connected</span>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ SQLite (local mode)")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 ── PREDICT
# ══════════════════════════════════════════════════════════════════════════════
if "🔍 Predict" in page:

    st.markdown('<p class="title-text">🏦 Loan Approval Predictor</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="subtitle-text">Applicant details bharein aur eligibility check karein</p>',
                unsafe_allow_html=True)

    if not model_loaded:
        st.error(f"❌ Model load nahi hua: {load_error}")
        st.stop()

    applicant_name = st.text_input(
        "👤 Applicant Name", placeholder="Full name likhein...")

    # Personal
    st.markdown('<div class="section-header">👤 Personal Information</div>',
                unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    age = c1.number_input("Age", 18, 80, 30)
    gender = c2.selectbox("Gender", ["Male", "Female"])
    marital = c3.selectbox("Marital Status", ["Single", "Married", "Divorced"])
    c1, c2 = st.columns(2)
    education = c1.selectbox("Education", [
                             "No Schooling", "High School", "Some College", "Bachelor's", "Master's", "PhD"])
    dependents = c2.number_input("Dependents", 0, 10, 0)

    # Employment
    st.markdown('<div class="section-header">💼 Employment & Income</div>',
                unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    employment = c1.selectbox(
        "Employment Type", ["Salaried", "Self-Employed", "Unemployed", "Part-time"])
    annual_income = c2.number_input(
        "Annual Income (₹)", 0, 10000000, 500000, step=10000)
    monthly_exp = c3.number_input(
        "Monthly Expenses (₹)", 0, 500000, 20000, step=1000)
    c1, c2 = st.columns(2)
    work_exp = c1.number_input("Work Experience (Yrs)", 0, 50, 5)
    job_stability = c2.selectbox(
        "Job Stability", ["Stable", "Unstable", "Contract"])

    # Loan
    st.markdown('<div class="section-header">🏠 Loan Details</div>',
                unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    loan_amount = c1.number_input(
        "Loan Amount (₹)", 1000, 10000000, 200000, step=5000)
    loan_tenure = c2.number_input("Tenure (Months)", 6, 360, 60, step=6)
    loan_purpose = c3.selectbox(
        "Purpose", ["Home", "Education", "Vehicle", "Personal", "Business", "Medical"])
    c1, c2 = st.columns(2)
    interest_rate = c1.slider("Interest Rate (%)", 1.0, 30.0, 10.5, 0.5)
    collateral = c2.selectbox("Collateral", ["Yes", "No"])

    # Credit
    st.markdown('<div class="section-header">📈 Credit & Financial History</div>',
                unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    credit_score = c1.number_input("Credit Score", 300, 900, 700, step=10)
    existing_loans = c2.number_input("Existing Loans", 0, 20, 0)
    missed_payments = c3.number_input("Missed Payments", 0, 50, 0)
    c1, c2, c3 = st.columns(3)
    debt_to_income = c1.slider("Debt-to-Income", 0.0, 1.0, 0.3, 0.01)
    savings = c2.number_input("Savings (₹)", 0, 10000000, 50000, step=5000)
    investment = c3.number_input("Investments (₹)", 0, 10000000, 0, step=5000)

    # Property
    st.markdown('<div class="section-header">🏘️ Property & Other</div>',
                unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    property_owned = c1.selectbox("Property Owned", ["Yes", "No"])
    residence_type = c2.selectbox(
        "Residence Type", ["Own", "Rented", "Family"])
    urban_rural = c3.selectbox("Area Type", ["Urban", "Rural", "Semi-Urban"])
    c1, c2 = st.columns(2)
    insurance = c1.selectbox("Life Insurance", ["Yes", "No"])
    credit_history = c2.selectbox("Good Credit History", ["Yes", "No"])

    st.markdown("---")

    # ── Feature Builder ────────────────────────────────────────────────────────
    def build_features():
        def yn(x): return 1 if x == "Yes" else 0
        marital_m = {"Single": 0, "Married": 1, "Divorced": 2}
        edu_m = {"No Schooling": 0, "High School": 1,
                 "Some College": 2, "Bachelor's": 3, "Master's": 4, "PhD": 5}
        emp_m = {"Salaried": 0, "Self-Employed": 1,
                 "Unemployed": 2, "Part-time": 3}
        pur_m = {"Home": 0, "Education": 1, "Vehicle": 2,
                 "Personal": 3, "Business": 4, "Medical": 5}
        stab_m = {"Stable": 1, "Unstable": 0, "Contract": 2}
        res_m = {"Own": 0, "Rented": 1, "Family": 2}
        area_m = {"Urban": 0, "Rural": 1, "Semi-Urban": 2}

        monthly_income = annual_income / 12
        r = interest_rate / 100 / 12
        emi = (loan_amount * r * (1+r)**loan_tenure) / \
            ((1+r)**loan_tenure - 1) if r > 0 else loan_amount / loan_tenure
        loan_to_income = loan_amount / (annual_income + 1)
        savings_ratio = savings / (annual_income + 1)
        net_surplus = monthly_income - monthly_exp - emi

        return np.array([
            age, 1 if gender == "Male" else 0, marital_m[marital], edu_m[education],
            dependents, emp_m[employment], annual_income, monthly_income,
            monthly_exp, work_exp, stab_m[job_stability], loan_amount,
            loan_tenure, pur_m[loan_purpose], interest_rate, yn(collateral),
            credit_score, existing_loans, missed_payments, debt_to_income,
            savings, investment, yn(property_owned), res_m[residence_type],
            area_m[urban_rural], yn(insurance), yn(credit_history),
            emi, loan_to_income, savings_ratio, net_surplus,
        ]).reshape(1, -1), emi, monthly_income

    # ── Predict Button ─────────────────────────────────────────────────────────
    if st.button("🔍 Check Loan Eligibility", use_container_width=True):
        with st.spinner("Analyzing application..."):
            try:
                X, emi, monthly_income = build_features()
                pred = model.predict(X)[0]
                proba = model.predict_proba(X)[0]
                approve_prob = round(proba[1] * 100, 2)
                reject_prob = round(proba[0] * 100, 2)
                result_label = "Approved" if pred == 1 else "Rejected"

                # ── Save to DB ─────────────────────────────────────────────────
                save_prediction({
                    "applicant_name": applicant_name or "Anonymous",
                    "age": age, "gender": gender, "marital_status": marital,
                    "education": education, "dependents": dependents,
                    "employment": employment, "annual_income": annual_income,
                    "monthly_expense": monthly_exp, "work_exp": work_exp,
                    "job_stability": job_stability, "loan_amount": loan_amount,
                    "loan_tenure": loan_tenure, "loan_purpose": loan_purpose,
                    "interest_rate": interest_rate, "collateral": collateral,
                    "credit_score": credit_score, "existing_loans": existing_loans,
                    "missed_payments": missed_payments, "debt_to_income": debt_to_income,
                    "savings": savings, "investments": investment,
                    "property_owned": property_owned, "residence_type": residence_type,
                    "area_type": urban_rural, "insurance": insurance,
                    "credit_history": credit_history, "emi": round(emi, 2),
                    "approve_prob": approve_prob, "reject_prob": reject_prob,
                    "prediction": result_label,
                })

                st.markdown("---")
                st.markdown("### 📋 Prediction Result")

                if pred == 1:
                    st.markdown("""
                    <div class="approved-banner">
                        <div class="result-icon">✅</div>
                        <div class="result-title">LOAN APPROVED!</div>
                        <div class="result-sub">Congratulations! Aapki application criteria meet karti hai.</div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="rejected-banner">
                        <div class="result-icon">❌</div>
                        <div class="result-title">LOAN REJECTED</div>
                        <div class="result-sub">Maafi chahte hain! Application required criteria meet nahi karti.</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**Approval Probability**")
                st.progress(int(approve_prob))
                st.markdown(
                    f'<p class="prob-label">✅ Approved: {approve_prob}% &nbsp;|&nbsp; ❌ Rejected: {reject_prob}%</p>', unsafe_allow_html=True)

                net_surplus = monthly_income - monthly_exp - emi
                st.markdown(
                    '<div class="section-header">📊 Financial Summary</div>', unsafe_allow_html=True)
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Monthly Income", f"₹{monthly_income:,.0f}")
                m2.metric("Est. EMI",       f"₹{emi:,.0f}")
                m3.metric("Net Surplus",    f"₹{net_surplus:,.0f}",
                          delta="Safe" if net_surplus > 0 else "Risk")
                m4.metric("Loan/Income",
                          f"{loan_amount/annual_income:.2f}x")

                st.markdown(
                    '<div class="section-header">💡 Improvement Tips</div>', unsafe_allow_html=True)
                tips = []
                if credit_score < 700:
                    tips.append("📈 Credit score 700+ karo.")
                if debt_to_income > 0.4:
                    tips.append("💳 Debt-to-Income ratio 40% se kam karo.")
                if missed_payments > 2:
                    tips.append("🗓️ Missed payments clear karo.")
                if net_surplus < 0:
                    tips.append(
                        "💰 Monthly expenses kam karo — EMI ke baad deficit hai.")
                if existing_loans > 2:
                    tips.append("🔒 Kuch existing loans close karo.")
                if not tips:
                    tips.append("🌟 Aapki financial profile strong hai!")
                for t in tips:
                    st.markdown(f"- {t}")

                st.success("✅ Record successfully database mein save ho gaya!")

            except Exception as e:
                st.error(f"⚠️ Error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 ── DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
elif "📊 Dashboard" in page:

    st.markdown('<p class="title-text">📊 Analytics Dashboard</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="subtitle-text">Database se live statistics</p>',
                unsafe_allow_html=True)

    stats = get_stats()
    df = get_all_predictions()

    # Summary cards
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📋 Total Cases",    stats["total"])
    c2.metric("✅ Approved",        stats["approved"])
    c3.metric("❌ Rejected",        stats["rejected"])
    c4.metric("📊 Avg Approval %", f"{stats['avg_prob']:.1f}%")

    c1, c2, c3 = st.columns(3)
    c1.metric("💳 Avg Credit Score", f"{stats['avg_credit']:.0f}")
    c2.metric("💰 Avg Loan Amount",  f"₹{stats['avg_loan']:,.0f}")
    approval_rate = round(
        stats["approved"] / stats["total"] * 100, 1) if stats["total"] > 0 else 0
    c3.metric("📈 Approval Rate",   f"{approval_rate}%")

    if not df.empty:
        st.markdown("---")
        st.markdown(
            '<div class="section-header">📉 Approval vs Rejection Trend</div>', unsafe_allow_html=True)

        df["created_at"] = pd.to_datetime(df["created_at"])
        trend = df.groupby(
            [df["created_at"].dt.date, "prediction"]).size().unstack(fill_value=0)
        st.bar_chart(trend)

        st.markdown(
            '<div class="section-header">🏦 Loan Purpose Distribution</div>', unsafe_allow_html=True)
        purpose_counts = df["loan_purpose"].value_counts()
        st.bar_chart(purpose_counts)

        st.markdown(
            '<div class="section-header">💳 Credit Score Distribution</div>', unsafe_allow_html=True)
        st.bar_chart(df["credit_score"].value_counts().sort_index())
    else:
        st.info("Abhi koi data nahi hai. Pehle kuch predictions karo! 🔍")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 ── ALL RECORDS
# ══════════════════════════════════════════════════════════════════════════════
elif "📋 All Records" in page:

    st.markdown('<p class="title-text">📋 All Prediction Records</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="subtitle-text">Database ke saare records yahan hain</p>',
                unsafe_allow_html=True)

    df = get_all_predictions()

    if df.empty:
        st.info("Koi records nahi hain abhi. Predict page pe jaao!")
    else:
        # Filter
        col1, col2 = st.columns(2)
        filter_result = col1.selectbox(
            "Filter by Result", ["All", "Approved", "Rejected"])
        search_name = col2.text_input("🔎 Search by Name", "")

        filtered = df.copy()
        if filter_result != "All":
            filtered = filtered[filtered["prediction"] == filter_result]
        if search_name:
            filtered = filtered[filtered["applicant_name"].str.contains(
                search_name, case=False, na=False)]

        st.markdown(f"**{len(filtered)} records** found")

        # Show table
        display_cols = ["id", "applicant_name", "prediction", "approve_prob",
                        "loan_amount", "credit_score", "annual_income", "created_at"]
        st.dataframe(
            filtered[display_cols].rename(columns={
                "id": "ID", "applicant_name": "Name", "prediction": "Result",
                "approve_prob": "Approve %", "loan_amount": "Loan (₹)",
                "credit_score": "Credit", "annual_income": "Income (₹)", "created_at": "Date"
            }),
            use_container_width=True,
            hide_index=True,
        )

        # CSV Download
        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download CSV",
            data=csv,
            file_name="loan_predictions.csv",
            mime="text/csv",
        )


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="text-align:center;color:rgba(255,255,255,0.3);font-size:0.78rem;">'
    '🏦 Loan Approval Predictor · KNN Model · PostgreSQL · Streamlit · Render</p>',
    unsafe_allow_html=True,
)
