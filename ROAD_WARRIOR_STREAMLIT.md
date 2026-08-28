# Road Warrior Offer Calculator — Streamlit

Deploy this branch in Streamlit Community Cloud using:

- Repository: `SoulfulGroove/dojo-dev-hub`
- Branch: `road-warrior-offer-calculator`
- Main file path: `app.py`

## Current calculator inputs

- Offer payout
- App estimated minutes
- Miles
- Reposition mode:
  - Highway = 1.0 min/mile
  - Mixed = 1.5 min/mile (default)
  - City / Slow = 2.0 min/mile

## Calculations

- Reposition minutes = miles × reposition factor
- Full-cycle minutes = app estimate + reposition minutes
- Baseline time budget = payout × 3.6
- Offer efficiency = baseline time budget ÷ full-cycle minutes
- Time buffer = baseline time budget − full-cycle minutes

100% efficiency represents the current $16.67/hour baseline (3.6 min/$).
