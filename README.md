# SaaS Product Analytics Platform

An end-to-end product analytics platform simulating the data science workflow at a B2C SaaS company — from raw event data to executive dashboards to ML-driven churn prediction.

**[Live Demo](https://saas-analytics-9ka6vue86lepme344qwmkz.streamlit.app)**

---

## What It Does

### 📊 Overview Dashboard
- KPI cards: Total Users, Paid Users, MRR, Churn Rate
- Monthly signups and cumulative user growth
- MRR breakdown by plan
- Acquisition channel distribution
- Daily Active Users (DAU) trend

### 🔻 Funnel & Cohort Analysis
- Full conversion funnel: Signup → Activation → Paid → Retained
- Monthly retention cohort heatmap (Month 0 to Month 6)
- Time-to-convert distribution by plan

### 🧪 A/B Testing Framework
- Experiment selector with 3 simulated experiments
- Statistical significance testing (z-test and Welch's t-test)
- Lift, p-value, and 95% confidence intervals
- Sample size calculator for future experiments

### 🤖 Churn Prediction (ML)
- LightGBM classifier trained on behavioral features
- ROC-AUC, Precision, Recall, F1 score
- SHAP feature importance for explainability
- At-risk user table with adjustable threshold
- Churn probability distribution by plan

---

## Tech Stack

| Layer | Tools |
|---|---|
| Data Simulation | Python, Faker, NumPy |
| Data Processing | Pandas |
| ML Model | LightGBM, Scikit-learn |
| Explainability | SHAP |
| Statistical Testing | SciPy |
| Visualization | Plotly |
| App Framework | Streamlit |
| Deployment | Streamlit Cloud |

---

## Run Locally

    git clone https://github.com/Karthik-Mudenahalli-Ashoka/saas-analytics.git
    cd saas-analytics
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    streamlit run app.py

---

## Project Structure

    saas-analytics/
    ├── app.py
    ├── requirements.txt
    ├── .python-version
    └── utils/
        ├── __init__.py
        └── simulator.py