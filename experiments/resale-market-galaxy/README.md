# Resale Market Galaxy — Dojo Experiment

Self-contained visualization experiment inside `dojo-dev-hub`.

## Isolation

Everything for this experiment lives under:

`/experiments/resale-market-galaxy/`

No existing root files or other dojo experiments are modified.

## Files

- `index.html` — page structure
- `styles.css` — visual design
- `data.js` — benchmark data
- `app.js` — interactive SVG visualization

## Visualization encoding

- X position: median hammer price
- Y position: percent of lots clearing $10+
- Bubble size: sample count
- Ring thickness: average bid count

The dashed $20 / 70% lines are operating reference guides, not statistical thresholds.

## Future experiments

- branded vs. unbranded toggle
- auction/date filters
- 3D opportunity field
- category heatmap
- routing/Sankey view
- JSON or generated data pipeline
