"""
utils/simulator.py
Generates realistic SaaS event data — users, events, subscriptions, A/B experiments.
Called by the Streamlit app on first load or when user clicks "Regenerate Data".
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker()

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
PLANS        = ["free", "starter", "pro", "enterprise"]
PLAN_PRICES  = {"free": 0, "starter": 29, "pro": 99, "enterprise": 499}

FEATURE_EVENTS = [
    "dashboard_view", "report_created", "report_shared", "export_csv",
    "api_call", "team_invite_sent", "integration_connected",
    "alert_created", "segment_created", "funnel_viewed",
    "insight_viewed", "data_source_added", "onboarding_step_completed",
    "billing_page_viewed", "support_ticket_opened",
]

EXPERIMENTS = {
    "onboarding_v2":      {"start": datetime(2023, 3, 1),  "end": datetime(2023, 6, 30)},
    "pricing_modal":      {"start": datetime(2023, 7, 1),  "end": datetime(2023, 10, 31)},
    "dashboard_redesign": {"start": datetime(2024, 1, 1),  "end": datetime(2024, 6, 30)},
}

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def _random_date(start, end):
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


# ─────────────────────────────────────────────
# USERS
# ─────────────────────────────────────────────
def generate_users(n, start_date, end_date, seed=42):
    np.random.seed(seed)
    random.seed(seed)
    Faker.seed(seed)

    channels   = ["organic_search", "paid_search", "referral", "product_hunt",
                  "social", "direct", "email_campaign"]
    channel_w  = [0.30, 0.20, 0.18, 0.08, 0.10, 0.09, 0.05]

    personas   = ["power_user", "casual_user", "at_risk", "churner", "new_user"]
    persona_w  = [0.15, 0.35, 0.20, 0.20, 0.10]

    company_sizes = ["1-10", "11-50", "51-200", "201-1000", "1000+"]
    cs_weights    = [0.25, 0.30, 0.22, 0.15, 0.08]

    industries = ["SaaS", "E-commerce", "Fintech", "Healthcare", "Media",
                  "Education", "Logistics", "Marketing Agency"]

    country_choices = ["US", "UK", "Canada", "Germany", "India",
                       "Australia", "France", "Brazil", "Singapore", "Netherlands"]
    country_weights = [0.40, 0.12, 0.08, 0.07, 0.08, 0.05, 0.05, 0.04, 0.03, 0.08]

    records = []
    for i in range(n):
        persona = np.random.choice(personas, p=persona_w)

        if persona == "power_user":
            plan = np.random.choice(PLANS, p=[0.05, 0.20, 0.50, 0.25])
        elif persona == "churner":
            plan = np.random.choice(PLANS, p=[0.50, 0.35, 0.13, 0.02])
        else:
            plan = np.random.choice(PLANS, p=[0.45, 0.30, 0.20, 0.05])

        records.append({
            "user_id":      f"usr_{i+1:05d}",
            "email":        fake.email(),
            "name":         fake.name(),
            "signup_date":  _random_date(start_date, end_date - timedelta(days=30)).date(),
            "channel":      np.random.choice(channels, p=channel_w),
            "plan":         plan,
            "persona":      persona,
            "company_size": np.random.choice(company_sizes, p=cs_weights),
            "industry":     random.choice(industries),
            "country":      np.random.choice(country_choices, p=country_weights),
            "is_trial":     random.random() < 0.30,
        })

    return pd.DataFrame(records)


# ─────────────────────────────────────────────
# EVENTS
# ─────────────────────────────────────────────
def generate_events(users_df, end_date):
    session_params = {
        "power_user":  (3.5, 1.2),
        "casual_user": (0.8, 0.5),
        "at_risk":     (0.3, 0.3),
        "churner":     (0.2, 0.2),
        "new_user":    (1.5, 0.8),
    }
    depth_params = {
        "power_user":  (8, 3),
        "casual_user": (3, 2),
        "at_risk":     (2, 1),
        "churner":     (2, 1),
        "new_user":    (4, 2),
    }
    feature_affinity = {
        "power_user":  ["report_created", "api_call", "segment_created",
                        "integration_connected", "alert_created", "funnel_viewed"],
        "casual_user": ["dashboard_view", "report_created", "export_csv", "insight_viewed"],
        "at_risk":     ["dashboard_view", "billing_page_viewed", "support_ticket_opened"],
        "churner":     ["billing_page_viewed", "support_ticket_opened", "dashboard_view"],
        "new_user":    ["onboarding_step_completed", "dashboard_view",
                        "report_created", "team_invite_sent"],
    }

    events = []
    for _, user in users_df.iterrows():
        persona    = user["persona"]
        signup_dt  = datetime.combine(user["signup_date"], datetime.min.time())
        active_days = (end_date - signup_dt).days

        if active_days <= 0:
            continue

        if persona == "churner":
            active_days = random.randint(7, min(90, active_days))
        elif persona == "at_risk":
            active_days = int(active_days * random.uniform(0.4, 0.7))
        else:
            active_days = min(active_days, 90)  # cap at 3 months
        mu, sigma     = session_params[persona]
        d_mu, d_sigma = depth_params[persona]
        affinity      = feature_affinity[persona]

        for day_offset in range(active_days):
            event_date    = signup_dt + timedelta(days=day_offset)
            weekday_mult  = 0.4 if event_date.weekday() >= 5 else 1.0
            month_mult    = 1.2 if event_date.month in [10, 11, 12] else 1.0
            sessions_today = np.random.poisson(max(0.01, mu * weekday_mult * month_mult))

            for _ in range(sessions_today):
                session_id    = fake.uuid4()
                session_start = event_date + timedelta(
                    hours=random.randint(8, 22),
                    minutes=random.randint(0, 59)
                )
                depth = max(1, int(np.random.normal(d_mu, d_sigma)))

                for idx in range(depth):
                    event_name = (
                        random.choice(affinity)
                        if random.random() < 0.80
                        else random.choice(FEATURE_EVENTS)
                    )
                    event_ts = session_start + timedelta(seconds=idx * random.randint(10, 180))
                    events.append({
                        "event_id":   fake.uuid4(),
                        "user_id":    user["user_id"],
                        "session_id": session_id,
                        "event_name": event_name,
                        "timestamp":  event_ts,
                        "date":       event_ts.date(),
                        "platform":   np.random.choice(
                            ["web", "mobile", "api"], p=[0.65, 0.25, 0.10]
                        ),
                        "country":    user["country"],
                    })

    return pd.DataFrame(events)


# ─────────────────────────────────────────────
# SUBSCRIPTIONS
# ─────────────────────────────────────────────
def generate_subscriptions(users_df, end_date):
    records = []

    for _, user in users_df.iterrows():
        signup_dt = datetime.combine(user["signup_date"], datetime.min.time())
        plan      = user["plan"]
        persona   = user["persona"]

        records.append({
            "subscription_id": fake.uuid4(),
            "user_id":         user["user_id"],
            "plan":            "free",
            "event_type":      "signup",
            "mrr":             0,
            "timestamp":       signup_dt,
        })

        if plan == "free":
            if persona == "churner" and random.random() < 0.6:
                records.append({
                    "subscription_id": fake.uuid4(),
                    "user_id":         user["user_id"],
                    "plan":            "free",
                    "event_type":      "churn",
                    "mrr":             0,
                    "timestamp":       signup_dt + timedelta(days=random.randint(14, 60)),
                })
            continue

        upgrade_dt = signup_dt + timedelta(days=random.randint(3, 45))
        if upgrade_dt > end_date:
            continue

        records.append({
            "subscription_id": fake.uuid4(),
            "user_id":         user["user_id"],
            "plan":            plan,
            "event_type":      "upgrade",
            "mrr":             PLAN_PRICES[plan],
            "timestamp":       upgrade_dt,
        })

        if persona == "churner":
            churn_dt = upgrade_dt + timedelta(days=random.randint(30, 120))
            if churn_dt <= end_date:
                records.append({
                    "subscription_id": fake.uuid4(),
                    "user_id":         user["user_id"],
                    "plan":            plan,
                    "event_type":      "churn",
                    "mrr":             0,
                    "timestamp":       churn_dt,
                })
        elif persona == "at_risk" and random.random() < 0.4:
            downgrade_dt    = upgrade_dt + timedelta(days=random.randint(60, 180))
            downgraded_plan = PLANS[max(0, PLANS.index(plan) - 1)]
            if downgrade_dt <= end_date:
                records.append({
                    "subscription_id": fake.uuid4(),
                    "user_id":         user["user_id"],
                    "plan":            downgraded_plan,
                    "event_type":      "downgrade",
                    "mrr":             PLAN_PRICES[downgraded_plan],
                    "timestamp":       downgrade_dt,
                })
        elif persona == "power_user" and random.random() < 0.25:
            idx = PLANS.index(plan)
            if idx < len(PLANS) - 1:
                expand_dt = upgrade_dt + timedelta(days=random.randint(90, 270))
                new_plan  = PLANS[idx + 1]
                if expand_dt <= end_date:
                    records.append({
                        "subscription_id": fake.uuid4(),
                        "user_id":         user["user_id"],
                        "plan":            new_plan,
                        "event_type":      "expansion",
                        "mrr":             PLAN_PRICES[new_plan],
                        "timestamp":       expand_dt,
                    })

    return pd.DataFrame(records).sort_values("timestamp").reset_index(drop=True)


# ─────────────────────────────────────────────
# A/B EXPERIMENTS
# ─────────────────────────────────────────────
def generate_ab_assignments(users_df):
    records = []
    for exp_name, exp in EXPERIMENTS.items():
        eligible = users_df[
            (pd.to_datetime(users_df["signup_date"]) >= exp["start"]) &
            (pd.to_datetime(users_df["signup_date"]) <= exp["end"])
        ]
        for _, user in eligible.iterrows():
            records.append({
                "experiment_name": exp_name,
                "user_id":         user["user_id"],
                "variant":         np.random.choice(["control", "treatment"]),
                "assigned_at":     _random_date(exp["start"], exp["end"]),
            })
    return pd.DataFrame(records)


# ─────────────────────────────────────────────
# MAIN ENTRY POINT (called by Streamlit)
# ─────────────────────────────────────────────
def generate_all(num_users=500, seed=42,
                 start_date=datetime(2023, 1, 1),
                 end_date=datetime(2024, 6, 30)):  # shorter date range too
    """
    Generate all four datasets and return as a dict of DataFrames.
    Called by app.py — results are cached in st.session_state.
    """
    np.random.seed(seed)
    random.seed(seed)
    Faker.seed(seed)

    users_df  = generate_users(num_users, start_date, end_date, seed)
    events_df = generate_events(users_df, end_date)
    subs_df   = generate_subscriptions(users_df, end_date)
    ab_df     = generate_ab_assignments(users_df)

    users_export = users_df.drop(columns=["persona"])

    return {
        "users":          users_export,
        "events":         events_df,
        "subscriptions":  subs_df,
        "ab_experiments": ab_df,
    }