"""
app.py — SaaS Product Analytics Platform
Main entry point. Handles data loading and sidebar navigation.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from utils.simulator import generate_all

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SaaS Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# LOAD / CACHE DATA
# ─────────────────────────────────────────────
@st.cache_data(show_spinner="Generating data — this takes ~30 seconds on first load...")
def load_data(num_users, seed):
    return generate_all(num_users=num_users, seed=seed)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.title("📊 SaaS Analytics")
    st.markdown("---")

    page = st.radio(
        "Navigation",
        ["🏠 Overview",
         "🔻 Funnel & Cohorts",
         "🧪 A/B Testing",
         "🤖 Churn Prediction"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.subheader("⚙️ Data Settings")
    num_users = st.slider("Number of Users", 1000, 10000, 5000, step=500)
    seed      = st.number_input("Random Seed", value=42, step=1)

    if st.button("🔄 Regenerate Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.caption("Built with Streamlit · Deployed on Streamlit Cloud")

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
data        = load_data(num_users, seed)
users       = data["users"]
events      = data["events"]
subs        = data["subscriptions"]
ab          = data["ab_experiments"]

# Ensure date types
users["signup_date"] = pd.to_datetime(users["signup_date"])
events["date"]       = pd.to_datetime(events["date"])
events["timestamp"]  = pd.to_datetime(events["timestamp"])
subs["timestamp"]    = pd.to_datetime(subs["timestamp"])

# ─────────────────────────────────────────────
# PAGE: OVERVIEW
# ─────────────────────────────────────────────
if page == "🏠 Overview":

    st.title("🏠 Overview")
    st.markdown("High-level product health metrics across the full date range.")
    st.markdown("---")

    # ── KPI Cards ──────────────────────────────
    total_users   = len(users)
    paid_users    = len(users[users["plan"] != "free"])
    total_events  = len(events)

    upgrades      = subs[subs["event_type"] == "upgrade"]
    total_mrr     = upgrades.groupby("user_id")["mrr"].last().sum()

    churns        = subs[subs["event_type"] == "churn"]
    churn_rate    = round(len(churns) / max(paid_users, 1) * 100, 1)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Users",    f"{total_users:,}")
    col2.metric("Paid Users",     f"{paid_users:,}")
    col3.metric("Total Events",   f"{total_events:,}")
    col4.metric("Total MRR",      f"${total_mrr:,.0f}")
    col5.metric("Churn Rate",     f"{churn_rate}%")

    st.markdown("---")

    # ── User Growth Over Time ───────────────────
    col_l, col_r = st.columns(2)

    with col_l:
        st.subheader("📈 User Signups Over Time")
        signups_by_month = (
            users.set_index("signup_date")
            .resample("ME")["user_id"]
            .count()
            .reset_index()
            .rename(columns={"signup_date": "month", "user_id": "signups"})
        )
        signups_by_month["cumulative"] = signups_by_month["signups"].cumsum()

        fig = go.Figure()
        fig.add_bar(
            x=signups_by_month["month"],
            y=signups_by_month["signups"],
            name="Monthly Signups",
            marker_color="#636EFA",
        )
        fig.add_scatter(
            x=signups_by_month["month"],
            y=signups_by_month["cumulative"],
            name="Cumulative Users",
            yaxis="y2",
            line=dict(color="#EF553B", width=2),
        )
        fig.update_layout(
            yaxis2=dict(overlaying="y", side="right", showgrid=False),
            legend=dict(orientation="h", y=1.1),
            margin=dict(t=20, b=20),
            height=320,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.subheader("💰 MRR by Plan")
        mrr_by_plan = (
            upgrades.groupby("plan")["mrr"]
            .sum()
            .reset_index()
            .sort_values("mrr", ascending=False)
        )
        fig2 = px.bar(
            mrr_by_plan, x="plan", y="mrr",
            color="plan",
            labels={"mrr": "Total MRR ($)", "plan": "Plan"},
            color_discrete_sequence=px.colors.qualitative.Plotly,
        )
        fig2.update_layout(showlegend=False, margin=dict(t=20, b=20), height=320)
        st.plotly_chart(fig2, use_container_width=True)

    # ── Acquisition Channels ────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📣 Acquisition Channels")
        channel_counts = users["channel"].value_counts().reset_index()
        channel_counts.columns = ["channel", "count"]
        fig3 = px.pie(
            channel_counts, names="channel", values="count",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig3.update_layout(margin=dict(t=20, b=20), height=320)
        st.plotly_chart(fig3, use_container_width=True)

    with col_b:
        st.subheader("🌍 Top Countries")
        country_counts = (
            users["country"].value_counts()
            .head(8)
            .reset_index()
        )
        country_counts.columns = ["country", "count"]
        fig4 = px.bar(
            country_counts, x="count", y="country",
            orientation="h",
            color="count",
            color_continuous_scale="Blues",
            labels={"count": "Users", "country": ""},
        )
        fig4.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(t=20, b=20),
            height=320,
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig4, use_container_width=True)

    # ── Daily Active Users ──────────────────────
    st.subheader("📅 Daily Active Users (DAU)")
    dau = (
        events.groupby("date")["user_id"]
        .nunique()
        .reset_index()
        .rename(columns={"user_id": "dau"})
    )
    fig5 = px.line(
        dau, x="date", y="dau",
        labels={"dau": "Daily Active Users", "date": ""},
        color_discrete_sequence=["#00CC96"],
    )
    fig5.update_layout(margin=dict(t=10, b=10), height=280)
    st.plotly_chart(fig5, use_container_width=True)

# ─────────────────────────────────────────────
# PLACEHOLDERS FOR OTHER PAGES
# ─────────────────────────────────────────────
elif page == "🔻 Funnel & Cohorts":
    st.title("🔻 Funnel & Cohort Analysis")
    st.markdown("Conversion funnel and retention cohorts across signup periods.")
    st.markdown("---")

    # ── CONVERSION FUNNEL ──────────────────────
    st.subheader("📉 Conversion Funnel")
    st.markdown("Tracks users from signup → first event → paid conversion.")

    total_signed_up   = len(users)

    # Activated = fired at least one non-dashboard event within 7 days of signup
    first_events = (
        events[events["event_name"] != "dashboard_view"]
        .groupby("user_id")["date"]
        .min()
        .reset_index()
        .rename(columns={"date": "first_event_date"})
    )
    activated_users = first_events.merge(users[["user_id", "signup_date"]], on="user_id")
    activated_users["days_to_activate"] = (
        pd.to_datetime(activated_users["first_event_date"]) -
        pd.to_datetime(activated_users["signup_date"])
    ).dt.days
    total_activated = len(activated_users[activated_users["days_to_activate"] <= 7])

    # Converted = upgraded to a paid plan
    converted_users = subs[subs["event_type"] == "upgrade"]["user_id"].nunique()

    # Retained = paid and not churned
    churned_users = subs[subs["event_type"] == "churn"]["user_id"].unique()
    retained_users = len(
        subs[
            (subs["event_type"] == "upgrade") &
            (~subs["user_id"].isin(churned_users))
        ]["user_id"].unique()
    )

    funnel_stages  = ["Signed Up", "Activated (7d)", "Converted to Paid", "Retained"]
    funnel_values  = [total_signed_up, total_activated, converted_users, retained_users]
    funnel_pcts    = [100] + [
        round(v / total_signed_up * 100, 1) for v in funnel_values[1:]
    ]

    fig_funnel = go.Figure(go.Funnel(
        y=funnel_stages,
        x=funnel_values,
        textinfo="value+percent initial",
        marker=dict(color=["#636EFA", "#EF553B", "#00CC96", "#AB63FA"]),
    ))
    fig_funnel.update_layout(margin=dict(t=20, b=20), height=380)
    st.plotly_chart(fig_funnel, use_container_width=True)

    # KPIs below funnel
    c1, c2, c3 = st.columns(3)
    c1.metric("Activation Rate",  f"{funnel_pcts[1]}%",  help="Activated within 7 days of signup")
    c2.metric("Conversion Rate",  f"{funnel_pcts[2]}%",  help="Upgraded to any paid plan")
    c3.metric("Retention Rate",   f"{funnel_pcts[3]}%",  help="Paid and not churned")

    st.markdown("---")

    # ── COHORT RETENTION HEATMAP ───────────────
    st.subheader("🗓️ Monthly Retention Cohorts")
    st.markdown("Each row = signup cohort. Each column = % still active N months later.")

    # Build cohort table
    users["cohort"] = users["signup_date"].dt.to_period("M")
    events["signup_date"] = events["user_id"].map(
        users.set_index("user_id")["signup_date"]
    )
    events["cohort"] = pd.to_datetime(events["signup_date"]).dt.to_period("M")
    events["event_period"] = events["date"].dt.to_period("M")
    events["period_number"] = (
        events["event_period"] - events["cohort"]
    ).apply(lambda x: x.n)

    cohort_data = (
        events[events["period_number"] >= 0]
        .groupby(["cohort", "period_number"])["user_id"]
        .nunique()
        .reset_index()
    )
    cohort_sizes = (
        users.groupby("cohort")["user_id"]
        .count()
        .reset_index()
        .rename(columns={"user_id": "cohort_size"})
    )
    cohort_data = cohort_data.merge(cohort_sizes, on="cohort")
    cohort_data["retention_rate"] = (
        cohort_data["user_id"] / cohort_data["cohort_size"] * 100
    ).round(1)

    # Pivot to heatmap shape — limit to 12 cohorts and 6 months for readability
    cohort_pivot = cohort_data.pivot_table(
        index="cohort", columns="period_number", values="retention_rate"
    )
    cohort_pivot = cohort_pivot.iloc[:, :7]   # months 0–6
    cohort_pivot = cohort_pivot.tail(12)       # last 12 cohorts
    cohort_pivot.index = cohort_pivot.index.astype(str)
    cohort_pivot.columns = [f"Month {c}" for c in cohort_pivot.columns]

    fig_cohort = px.imshow(
        cohort_pivot,
        text_auto=".1f",
        color_continuous_scale="Blues",
        aspect="auto",
        labels=dict(color="Retention %"),
    )
    fig_cohort.update_layout(
        margin=dict(t=20, b=20),
        height=420,
        xaxis_title="",
        yaxis_title="Signup Cohort",
        coloraxis_colorbar=dict(title="Ret. %"),
    )
    st.plotly_chart(fig_cohort, use_container_width=True)
    st.caption("Month 0 = signup month (always ~100%). Values are % of cohort still active.")

    st.markdown("---")

    # ── TIME TO CONVERT ────────────────────────
    st.subheader("⏱️ Time to Convert (Days from Signup to First Upgrade)")

    upgrades_with_signup = (
        subs[subs["event_type"] == "upgrade"]
        .merge(users[["user_id", "signup_date"]], on="user_id")
    )
    upgrades_with_signup["days_to_convert"] = (
        upgrades_with_signup["timestamp"] - upgrades_with_signup["signup_date"]
    ).dt.days

    fig_ttc = px.histogram(
        upgrades_with_signup[upgrades_with_signup["days_to_convert"] <= 180],
        x="days_to_convert",
        nbins=40,
        color="plan",
        labels={"days_to_convert": "Days to First Upgrade", "count": "Users"},
        color_discrete_sequence=px.colors.qualitative.Plotly,
        barmode="overlay",
        opacity=0.75,
    )
    fig_ttc.update_layout(margin=dict(t=20, b=20), height=320)
    st.plotly_chart(fig_ttc, use_container_width=True)
    st.caption("Distribution of how long users take to upgrade, broken down by plan.")

elif page == "🧪 A/B Testing":
    st.title("🧪 A/B Testing")
    st.markdown("Statistical analysis of product experiments — lift, p-values, and confidence intervals.")
    st.markdown("---")

    import scipy.stats as stats
    import numpy as np

    # ── EXPERIMENT SELECTOR ────────────────────
    exp_names = ab["experiment_name"].unique().tolist()
    selected_exp = st.selectbox("Select Experiment", exp_names)

    exp_users = ab[ab["experiment_name"] == selected_exp]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Users in Experiment", f"{len(exp_users):,}")
    col2.metric("Control Group",   f"{len(exp_users[exp_users['variant'] == 'control']):,}")
    col3.metric("Treatment Group", f"{len(exp_users[exp_users['variant'] == 'treatment']):,}")

    st.markdown("---")

    # ── METRIC SELECTOR ───────────────────────
    st.subheader("📐 Choose a Success Metric")
    metric_choice = st.radio(
        "Metric",
        ["Conversion to Paid", "Activation Rate (7-day)", "Avg Events per User"],
        horizontal=True,
    )

    # Merge experiment users with users and events
    exp_with_users = exp_users.merge(users[["user_id", "signup_date", "plan"]], on="user_id", how="left")

    control   = exp_with_users[exp_with_users["variant"] == "control"]
    treatment = exp_with_users[exp_with_users["variant"] == "treatment"]

    def compute_metric(group, metric):
        if metric == "Conversion to Paid":
            converted = (group["plan"] != "free").astype(int)
            return converted.values, converted.mean()

        elif metric == "Activation Rate (7-day)":
            first_ev = (
                events[events["event_name"] != "dashboard_view"]
                .groupby("user_id")["date"].min()
                .reset_index()
                .rename(columns={"date": "first_event_date"})
            )
            merged = group.merge(first_ev, on="user_id", how="left")
            merged["days"] = (
                pd.to_datetime(merged["first_event_date"]) -
                pd.to_datetime(merged["signup_date"])
            ).dt.days
            activated = (merged["days"] <= 7).fillna(False).astype(int)
            return activated.values, activated.mean()

        elif metric == "Avg Events per User":
            event_counts = (
                events.groupby("user_id")["event_id"]
                .count()
                .reset_index()
                .rename(columns={"event_id": "event_count"})
            )
            merged = group.merge(event_counts, on="user_id", how="left").fillna(0)
            return merged["event_count"].values, merged["event_count"].mean()

    ctrl_vals,  ctrl_mean  = compute_metric(control,   metric_choice)
    treat_vals, treat_mean = compute_metric(treatment, metric_choice)

    lift = ((treat_mean - ctrl_mean) / max(ctrl_mean, 1e-9)) * 100

    # Statistical test
    if metric_choice in ["Conversion to Paid", "Activation Rate (7-day)"]:
        # Two-proportion z-test
        n_ctrl  = len(ctrl_vals)
        n_treat = len(treat_vals)
        p_ctrl  = ctrl_mean
        p_treat = treat_mean
        p_pool  = (ctrl_vals.sum() + treat_vals.sum()) / (n_ctrl + n_treat)
        se      = np.sqrt(p_pool * (1 - p_pool) * (1/n_ctrl + 1/n_treat))
        z_stat  = (p_treat - p_ctrl) / max(se, 1e-9)
        p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
        ci_low  = (p_treat - p_ctrl) - 1.96 * se
        ci_high = (p_treat - p_ctrl) + 1.96 * se
        ci_label = f"{ci_low*100:+.2f}% to {ci_high*100:+.2f}%"
    else:
        # Welch's t-test
        t_stat, p_value = stats.ttest_ind(treat_vals, ctrl_vals, equal_var=False)
        se      = np.sqrt(np.var(treat_vals)/len(treat_vals) + np.var(ctrl_vals)/len(ctrl_vals))
        ci_low  = (treat_mean - ctrl_mean) - 1.96 * se
        ci_high = (treat_mean - ctrl_mean) + 1.96 * se
        ci_label = f"{ci_low:+.2f} to {ci_high:+.2f} events"

    significant = p_value < 0.05

    # ── RESULTS ────────────────────────────────
    st.subheader("📊 Results")

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Control",   f"{ctrl_mean*100:.2f}%" if metric_choice != "Avg Events per User" else f"{ctrl_mean:.1f}")
    r2.metric("Treatment", f"{treat_mean*100:.2f}%" if metric_choice != "Avg Events per User" else f"{treat_mean:.1f}",
              delta=f"{lift:+.1f}% lift")
    r3.metric("p-value",   f"{p_value:.4f}", help="< 0.05 = statistically significant")
    r4.metric("Significant?", "✅ Yes" if significant else "❌ No")

    # Confidence interval bar
    fig_ci = go.Figure()
    fig_ci.add_trace(go.Bar(
        x=["Control", "Treatment"],
        y=[ctrl_mean, treat_mean],
        error_y=dict(
            type="constant",
            value=(treat_mean - ctrl_mean) if not significant else abs(treat_mean - ctrl_mean),
            visible=False,
        ),
        marker_color=["#636EFA", "#00CC96" if significant else "#EF553B"],
        text=[f"{ctrl_mean*100:.2f}%" if metric_choice != "Avg Events per User" else f"{ctrl_mean:.1f}",
              f"{treat_mean*100:.2f}%" if metric_choice != "Avg Events per User" else f"{treat_mean:.1f}"],
        textposition="outside",
    ))
    fig_ci.update_layout(
        title=f"{metric_choice} — Control vs Treatment",
        yaxis_title=metric_choice,
        margin=dict(t=40, b=20),
        height=340,
        showlegend=False,
    )
    st.plotly_chart(fig_ci, use_container_width=True)

    # Interpretation box
    if significant:
        st.success(
            f"✅ **Statistically significant result** (p = {p_value:.4f}). "
            f"Treatment shows a **{lift:+.1f}% lift** over control. "
            f"95% CI: {ci_label}. **Recommendation: ship the treatment.**"
        )
    else:
        st.warning(
            f"⚠️ **Not statistically significant** (p = {p_value:.4f}). "
            f"Observed lift: {lift:+.1f}%. "
            f"95% CI: {ci_label}. **Recommendation: run longer or redesign the experiment.**"
        )

    st.markdown("---")

    # ── DAILY CONVERSION TREND BY VARIANT ─────
    st.subheader("📈 Daily Conversion Trend by Variant")

    upgrades_exp = (
        subs[subs["event_type"] == "upgrade"]
        .merge(exp_users, on="user_id", how="inner")
    )
    daily_conv = (
        upgrades_exp.groupby([upgrades_exp["timestamp"].dt.date, "variant"])["user_id"]
        .count()
        .reset_index()
        .rename(columns={"timestamp": "date", "user_id": "conversions"})
    )
    fig_trend = px.line(
        daily_conv, x="date", y="conversions", color="variant",
        color_discrete_map={"control": "#636EFA", "treatment": "#00CC96"},
        labels={"conversions": "Daily Conversions", "date": ""},
    )
    fig_trend.update_layout(margin=dict(t=20, b=20), height=300)
    st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown("---")

    # ── SAMPLE SIZE CALCULATOR ─────────────────
    st.subheader("🔢 Sample Size Calculator")
    st.markdown("How many users do you need for a future experiment?")

    sc1, sc2, sc3 = st.columns(3)
    baseline    = sc1.number_input("Baseline Rate (%)", value=20.0, step=0.5) / 100
    mde         = sc2.number_input("Min. Detectable Effect (%)", value=5.0, step=0.5) / 100
    power       = sc3.slider("Statistical Power", 0.70, 0.95, 0.80, step=0.05)

    alpha    = 0.05
    z_alpha  = stats.norm.ppf(1 - alpha / 2)
    z_beta   = stats.norm.ppf(power)
    p2       = baseline + mde
    p_bar    = (baseline + p2) / 2
    n        = int(np.ceil(
        2 * p_bar * (1 - p_bar) * ((z_alpha + z_beta) ** 2) / (mde ** 2)
    ))

    st.info(f"You need **{n:,} users per variant** ({n*2:,} total) to detect a {mde*100:.1f}% lift from a {baseline*100:.1f}% baseline at {power*100:.0f}% power.")
elif page == "🤖 Churn Prediction":
    st.title("🤖 Churn Prediction")
    st.markdown("LightGBM churn model with SHAP explainability — trained on simulated user behavior.")
    st.markdown("---")

    import lightgbm as lgb
    import shap
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import (
        classification_report, roc_auc_score,
        roc_curve, confusion_matrix,
    )
    import numpy as np

    # ── FEATURE ENGINEERING ────────────────────
    @st.cache_data(show_spinner="Building features & training model...")
    def build_and_train(_users, _events, _subs, seed):

        # Who churned?
        churned_ids = set(_subs[_subs["event_type"] == "churn"]["user_id"].unique())

        # Event features per user
        ev_feats = (
            _events.groupby("user_id")
            .agg(
                total_events   = ("event_id",    "count"),
                unique_events  = ("event_name",  "nunique"),
                active_days    = ("date",         "nunique"),
                sessions       = ("session_id",   "nunique"),
                api_calls      = ("event_name",   lambda x: (x == "api_call").sum()),
                reports_created= ("event_name",   lambda x: (x == "report_created").sum()),
                support_tickets= ("event_name",   lambda x: (x == "support_ticket_opened").sum()),
                billing_views  = ("event_name",   lambda x: (x == "billing_page_viewed").sum()),
                mobile_events  = ("platform",     lambda x: (x == "mobile").sum()),
            )
            .reset_index()
        )

        # Subscription features
        sub_feats = (
            _subs[_subs["event_type"] == "upgrade"]
            .groupby("user_id")
            .agg(mrr=("mrr", "last"))
            .reset_index()
        )

        # Merge everything
        df = _users.merge(ev_feats, on="user_id", how="left").merge(sub_feats, on="user_id", how="left")
        df["churned"] = df["user_id"].isin(churned_ids).astype(int)

        # Days since signup
        df["days_since_signup"] = (
            pd.Timestamp("2024-12-31") - pd.to_datetime(df["signup_date"])
        ).dt.days

        # Encode categoricals
        df["plan_encoded"]    = df["plan"].map({"free": 0, "starter": 1, "pro": 2, "enterprise": 3})
        df["channel_encoded"] = df["channel"].astype("category").cat.codes
        df["country_encoded"] = df["country"].astype("category").cat.codes

        df = df.fillna(0)

        FEATURES = [
            "total_events", "unique_events", "active_days", "sessions",
            "api_calls", "reports_created", "support_tickets", "billing_views",
            "mobile_events", "mrr", "days_since_signup",
            "plan_encoded", "channel_encoded", "country_encoded",
        ]

        X = df[FEATURES]
        y = df["churned"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=seed, stratify=y
        )

        model = lgb.LGBMClassifier(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=6,
            num_leaves=31,
            random_state=seed,
            verbose=-1,
        )
        model.fit(X_train, y_train)

        y_pred_proba = model.predict_proba(X_test)[:, 1]
        y_pred       = model.predict(X_test)
        auc          = roc_auc_score(y_test, y_pred_proba)
        fpr, tpr, _  = roc_curve(y_test, y_pred_proba)
        cm           = confusion_matrix(y_test, y_pred)
        report       = classification_report(y_test, y_pred, output_dict=True)

        # SHAP values
        explainer   = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_test)
        if isinstance(shap_values, list):
            shap_values = shap_values[1]

        # Churn probability for all users
        df["churn_probability"] = model.predict_proba(X[FEATURES])[:, 1]

        return {
            "model":        model,
            "auc":          auc,
            "fpr":          fpr,
            "tpr":          tpr,
            "cm":           cm,
            "report":       report,
            "shap_values":  shap_values,
            "X_test":       X_test,
            "features":     FEATURES,
            "user_scores":  df[["user_id", "plan", "mrr", "total_events",
                                "active_days", "churn_probability"]],
        }

    result = build_and_train(users, events, subs, seed=42)

    # ── MODEL PERFORMANCE ──────────────────────
    st.subheader("📈 Model Performance")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("ROC-AUC",   f"{result['auc']:.3f}")
    m2.metric("Precision", f"{result['report']['1']['precision']:.3f}")
    m3.metric("Recall",    f"{result['report']['1']['recall']:.3f}")
    m4.metric("F1 Score",  f"{result['report']['1']['f1-score']:.3f}")

    col_roc, col_cm = st.columns(2)

    with col_roc:
        st.markdown("**ROC Curve**")
        fig_roc = go.Figure()
        fig_roc.add_trace(go.Scatter(
            x=result["fpr"], y=result["tpr"],
            mode="lines", name=f"AUC = {result['auc']:.3f}",
            line=dict(color="#636EFA", width=2),
        ))
        fig_roc.add_trace(go.Scatter(
            x=[0, 1], y=[0, 1],
            mode="lines", name="Random",
            line=dict(color="gray", dash="dash"),
        ))
        fig_roc.update_layout(
            xaxis_title="False Positive Rate",
            yaxis_title="True Positive Rate",
            margin=dict(t=20, b=20), height=320,
            legend=dict(x=0.6, y=0.1),
        )
        st.plotly_chart(fig_roc, use_container_width=True)

    with col_cm:
        st.markdown("**Confusion Matrix**")
        cm = result["cm"]
        fig_cm = px.imshow(
            cm,
            text_auto=True,
            x=["Predicted: Stay", "Predicted: Churn"],
            y=["Actual: Stay",    "Actual: Churn"],
            color_continuous_scale="Blues",
        )
        fig_cm.update_layout(margin=dict(t=20, b=20), height=320)
        st.plotly_chart(fig_cm, use_container_width=True)

    st.markdown("---")

    # ── SHAP FEATURE IMPORTANCE ────────────────
    st.subheader("🔍 SHAP Feature Importance")
    st.markdown("Which features drive churn predictions the most?")

    shap_vals   = result["shap_values"]
    features    = result["features"]
    mean_shap   = np.abs(shap_vals).mean(axis=0)
    shap_df     = (
        pd.DataFrame({"feature": features, "mean_shap": mean_shap})
        .sort_values("mean_shap", ascending=True)
    )

    fig_shap = px.bar(
        shap_df, x="mean_shap", y="feature",
        orientation="h",
        color="mean_shap",
        color_continuous_scale="Reds",
        labels={"mean_shap": "Mean |SHAP Value|", "feature": ""},
    )
    fig_shap.update_layout(
        coloraxis_showscale=False,
        margin=dict(t=20, b=20),
        height=420,
    )
    st.plotly_chart(fig_shap, use_container_width=True)
    st.caption("Higher SHAP value = stronger influence on churn prediction.")

    st.markdown("---")

    # ── AT-RISK USER TABLE ─────────────────────
    st.subheader("🚨 At-Risk Users")
    st.markdown("Users with highest predicted churn probability — prioritize for intervention.")

    threshold = st.slider("Churn Probability Threshold", 0.50, 0.95, 0.70, step=0.05)

    at_risk = (
        result["user_scores"]
        [result["user_scores"]["churn_probability"] >= threshold]
        .sort_values("churn_probability", ascending=False)
        .head(50)
        .reset_index(drop=True)
    )
    at_risk.index += 1
    at_risk["churn_probability"] = at_risk["churn_probability"].map("{:.1%}".format)
    at_risk["mrr"]               = at_risk["mrr"].map("${:.0f}".format)

    st.dataframe(
        at_risk.rename(columns={
            "user_id":           "User ID",
            "plan":              "Plan",
            "mrr":               "MRR",
            "total_events":      "Total Events",
            "active_days":       "Active Days",
            "churn_probability": "Churn Probability",
        }),
        use_container_width=True,
        height=400,
    )
    st.caption(f"Showing top 50 users above {threshold:.0%} churn probability threshold.")

    st.markdown("---")

    # ── CHURN PROBABILITY DISTRIBUTION ─────────
    st.subheader("📊 Churn Probability Distribution by Plan")

    fig_dist = px.violin(
        result["user_scores"],
        x="plan", y="churn_probability",
        color="plan",
        box=True,
        points=False,
        category_orders={"plan": ["free", "starter", "pro", "enterprise"]},
        color_discrete_sequence=px.colors.qualitative.Plotly,
        labels={"churn_probability": "Churn Probability", "plan": "Plan"},
    )
    fig_dist.update_layout(
        showlegend=False,
        margin=dict(t=20, b=20),
        height=360,
    )
    st.plotly_chart(fig_dist, use_container_width=True)