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

## 🏢 Enterprise Application

This platform demonstrates the exact analytics capabilities that a large-scale B2C company — such as a mobility or rental services provider — would use to drive data-informed decisions:

- **Churn Prediction** — Identify which customers are at risk of disengaging before they leave, enabling proactive retention outreach
- **Cohort Retention Analysis** — Understand how different customer segments retain over time, broken down by acquisition channel or plan
- **A/B Testing Framework** — Run statistically rigorous experiments to test pricing changes, UX improvements, or promotional offers with confidence intervals and p-values
- **Executive KPI Dashboard** — Surface MRR, DAU, churn rate, and conversion funnel metrics in a single view for leadership decision-making

> Built to simulate the data science workflow inside a real B2C operations team — from raw event ingestion to ML-driven customer intelligence.

---

## Run Locally

```bash
git clone https://github.com/Karthik-Mudenahalli-Ashoka/saas-analytics.git
cd saas-analytics
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

---

## Project Structure

```
saas-analytics/
├── app.py
├── requirements.txt
├── .python-version
└── utils/
    ├── __init__.py
    └── simulator.py
```

---

## 👤 Author

**Karthik Mudenahalli Ashoka**  
MS in Applied Artificial Intelligence, Stevens Institute of Technology  
[LinkedIn](https://www.linkedin.com/in/m-a-karthik/) | [GitHub](https://github.com/Karthik-Mudenahalli-Ashoka)
