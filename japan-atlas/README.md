# Living Atlas of Japan · 1580–1650

An interactive, evidence-aware prototype for historical geography during Miyamoto Musashi's lifetime, under `/japan-atlas/`.

## What this first version does

- Shows a modern terrain/topographical map with **indicative modern** locator pins for historically named places and districts.
- Lists 44 candidate place and route-node records from the research package, with the historical province, date range, cited source IDs, and an unresolved-questions note.
- Filters places by name, evidence grade, and broad activity categories (mining, marine, farming, forestry, commercial, transport, institutional).
- Draws selected **schematic** relationships from six commodity-chain research records, distinguished as supported broader systems (B) or provisional leads (C). The visible straight-line links are **connections, not reconstructive historical route geometry**.
- Shows a two-location evidence matrix as a starting point for *zebra-puzzle logic*. "Recorded" means a keyword classification found the activity in the underlying source-derived record; "Unknown" is **not** proof that the activity was absent.
- Links back to the relevant source catalog entries.

## What this version does NOT claim

- The map does **not** show historical provincial polygons, exact historical settlement centers, dated river courses, or georeferenced historical boundaries.
- Its HTML contains **separate approximate modern orientation coordinates**. The source-research CSV and GeoJSON deliberately have no historical geometry. Never use the modern pin coordinates as reconstructed positions of historical settlements or production sites.
- It does **not** assert complete local resource inventories, absence of particular resources, universal trade routes, or populations.
- No A-grade locality was established in the underlying research. There are 23 provisional B records and 21 C records.
- Commodity-chain evidence varies; of six records, three are provisional.
- The study period runs 1580–1650, but some descriptions or identified source material are later. The dates and limitations need claim-level verification.
- It does not automatically assert presence in 1585, 1600, 1615, or 1645 merely because a locality appears in the gazetteer.

## Local structure

- `index.html`: interactive interface (Leaflet, Esri/OSM contemporary terrain)
- `atlas-data.js`: generated static research tables, embedded for easy static hosting
- `data/`: source spreadsheets reproduced from the user-provided research package

No build system or API key is required. Static hosting works with GitHub Pages. Terrain layers and Leaflet scripts require internet access.

## Source-table meanings

The source catalogue separates inspected collection access points from leads; a linked URL does not mean every associated historical assertion is verified. For more details see the research package's README.

## Intended next refinement

The right next step is a **dated, location-specific resource and claim ledger**:

`location → commodity/resource → status {local production | external supply | verified absence | not established} → period → source → passage → confidence`

Then cross-comparison and logical dependencies can be computed without turning silence in a historical source into a claim of nonexistence. Historical georeferencing, province overlays, and individually attested transport routes should come afterward.

The goal is a source-led map that can answer: *What was available here? What came from elsewhere? Which connections and institutions made life possible in this place and year?*
