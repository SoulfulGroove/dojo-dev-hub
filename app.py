import streamlit as st

st.set_page_config(
    page_title="Road Warrior Offer Calculator",
    page_icon="⚔️",
    layout="centered",
)

BASELINE_MIN_PER_DOLLAR = 3.6
BASELINE_HOURLY_RATE = 60 / BASELINE_MIN_PER_DOLLAR

REPOSITION_MODES = {
    "Highway": 1.0,
    "Mixed": 1.5,
    "City / Slow": 2.0,
}

st.markdown(
    """
    <style>
    .block-container {max-width: 900px; padding-top: 1.75rem; padding-bottom: 3rem;}
    .rw-eyebrow {font-size:.74rem; letter-spacing:.12em; text-transform:uppercase; opacity:.65; font-weight:700;}
    .rw-title {font-size:2rem; font-weight:800; line-height:1.1; margin:.25rem 0 .35rem 0;}
    .rw-subtitle {opacity:.68; margin-bottom:1.1rem;}
    .rw-card {border:1px solid rgba(128,128,128,.28); border-radius:16px; padding:1rem 1.05rem; margin:.45rem 0;}
    .rw-label {font-size:.72rem; letter-spacing:.08em; text-transform:uppercase; opacity:.62; font-weight:700;}
    .rw-value {font-size:1.65rem; font-weight:800; line-height:1.1; margin-top:.25rem;}
    .rw-sub {font-size:.82rem; opacity:.62; margin-top:.2rem;}
    .rw-good {color:#36b66a;}
    .rw-warn {color:#d29b2e;}
    .rw-bad {color:#db5c5c;}
    .rw-summary {border-top:1px solid rgba(128,128,128,.24); margin-top:.8rem; padding-top:.8rem; font-weight:650;}
    div[data-testid="stMetricValue"] {font-size:1.55rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="rw-eyebrow">Road Warrior • Offer Evaluation</div>', unsafe_allow_html=True)
st.markdown('<div class="rw-title">Offer Efficiency Calculator</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="rw-subtitle">Evaluate the whole offer cycle against the 3.6 min/$ baseline.</div>',
    unsafe_allow_html=True,
)

with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        payout = st.number_input("Offer payout ($)", min_value=0.0, value=21.72, step=0.01, format="%.2f")
    with c2:
        app_minutes = st.number_input("App estimated time (min)", min_value=0.0, value=33.0, step=1.0)
    with c3:
        miles = st.number_input("Miles", min_value=0.0, value=8.6, step=0.1, format="%.1f")

    reposition_mode = st.segmented_control(
        "Reposition mode",
        options=list(REPOSITION_MODES.keys()),
        default="Mixed",
        selection_mode="single",
        help="Highway = 1.0 min/mi • Mixed = 1.5 min/mi • City / Slow = 2.0 min/mi",
    )

factor = REPOSITION_MODES.get(reposition_mode or "Mixed", 1.5)
reposition_minutes = miles * factor
full_cycle_minutes = app_minutes + reposition_minutes
baseline_budget_minutes = payout * BASELINE_MIN_PER_DOLLAR

valid = payout > 0 and full_cycle_minutes > 0

if valid:
    efficiency = baseline_budget_minutes / full_cycle_minutes
    efficiency_pct = efficiency * 100
    efficiency_gain_pct = (efficiency - 1) * 100
    time_buffer = baseline_budget_minutes - full_cycle_minutes
    equivalent_hourly = payout / full_cycle_minutes * 60
    minutes_per_dollar = full_cycle_minutes / payout
    dollars_per_minute = payout / full_cycle_minutes
    budget_consumed_pct = full_cycle_minutes / baseline_budget_minutes * 100
else:
    efficiency = efficiency_pct = efficiency_gain_pct = 0
    time_buffer = equivalent_hourly = minutes_per_dollar = dollars_per_minute = 0
    budget_consumed_pct = 0


def duration_text(minutes: float) -> str:
    total = int(round(minutes))
    hours, mins = divmod(total, 60)
    if hours:
        return f"{hours}h {mins:02d}m"
    return f"{mins}m"


def efficiency_label(pct: float) -> tuple[str, str]:
    if pct < 100:
        return "Below baseline", "rw-bad"
    if pct < 120:
        return "Qualifying", "rw-warn"
    if pct < 150:
        return "Solid", "rw-warn"
    if pct < 180:
        return "Strong", "rw-good"
    return "Exceptional", "rw-good"


if not valid:
    st.info("Enter a payout and a non-zero time estimate to evaluate the offer.")
else:
    label, css_class = efficiency_label(efficiency_pct)

    st.markdown(
        f"**Time budget consumed:** {budget_consumed_pct:.0f}%  •  "
        f"**Status:** {label}"
    )
    st.progress(min(max(budget_consumed_pct / 100, 0.0), 1.0))

    a, b, c, d = st.columns(4)
    with a:
        st.metric("Full-cycle time", f"{full_cycle_minutes:.1f} min", duration_text(full_cycle_minutes))
    with b:
        st.metric("Baseline budget", f"{baseline_budget_minutes:.1f} min", duration_text(baseline_budget_minutes))
    with c:
        st.metric("Offer efficiency", f"{efficiency_pct:.0f}%", f"{efficiency_gain_pct:+.0f}% vs baseline")
    with d:
        st.metric("Time buffer", f"{time_buffer:+.1f} min", "vs 100% baseline")

    with st.container(border=True):
        e, f, g, h = st.columns(4)
        with e:
            st.metric("Reposition time", f"{reposition_minutes:.1f} min", f"{factor:.1f} min/mi")
        with f:
            st.metric("Equivalent rate", f"${equivalent_hourly:.2f}/hr", f"Baseline ${BASELINE_HOURLY_RATE:.2f}/hr")
        with g:
            st.metric("Minutes / $", f"{minutes_per_dollar:.2f}", "Lower is better")
        with h:
            st.metric("$ / minute", f"${dollars_per_minute:.2f}", "Higher is better")

        st.markdown(
            f"**${payout:.2f} over {duration_text(full_cycle_minutes)} is {efficiency_pct:.0f}% efficient "
            f"and creates {time_buffer:+.0f} minutes of buffer.**"
        )
        st.caption(
            "Efficiency = (payout × 3.6) ÷ full-cycle minutes. "
            "100% means the offer exactly matches the $16.67/hr operating baseline."
        )

with st.expander("How the calculation works"):
    st.markdown(
        f"""
- **Reposition minutes** = miles × selected driving factor
- **Full-cycle minutes** = app estimated minutes + reposition minutes
- **Baseline time budget** = payout × {BASELINE_MIN_PER_DOLLAR}
- **Offer efficiency** = baseline time budget ÷ full-cycle minutes
- **Time buffer** = baseline time budget − full-cycle minutes

Driving factors:
- Highway: **1.0 min/mile**
- Mixed: **1.5 min/mile**
- City / Slow: **2.0 min/mile**
        """
    )
