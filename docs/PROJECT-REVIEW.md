# EcoRestore v2 — project review

## Idea and contribution

EcoRestore helps researchers and restoration planners identify degraded zones, explain priorities and compare intervention assumptions. Its strongest defensible contribution is an auditable decision workflow: environmental observations → transparent score → intervention hypothesis → budget shortlist → field review → measured outcomes.

The original app is a Streamlit/Python research prototype with ingestion, feature engineering, priority scoring, supervised models, GIS, intervention rules, simulation, reports and SQLite. The supplied `frontend` contained only cached dependencies, with no usable app source. The new Vite web application adds a deployable browser experience without removing those original Python capabilities.

## Findings from the uploaded source

- The sample CSV contains 1,000 records labelled `SYNTHETIC_DEMO`. It is not verified field data. Coordinates do not establish real site boundaries or land suitability.
- `src/model_training.py` explicitly states that supervised targets derive from the priority baseline. Accuracy against these targets measures rule approximation, not independently validated ecological prediction.
- The original classification used integer intervals (0–25, 26–50, etc.), allowing decimal scores such as 50.5 to fall through to LOW. This was fixed in the Python engine and covered by a regression test. The browser engine uses continuous cutoffs.
- Original models and SQLite remain in the downloadable archive for continuity but are ignored by Git. Do not load untrusted serialized models. Browser deployment neither loads them nor publishes the database.

## Implemented improvements

1. Responsive overview, coordinate explorer, search and priority filtering, CSV export and per-zone weighted contribution explanations.
2. Supabase client integration: email/password registration, sign-in, email-confirmation callback via PKCE, sign-out, password-reset request and password update form.
3. Protected scenario studio and saved-plan routes. Route access verifies the current user with Supabase; database ownership policies provide actual data protection.
4. Recovery-gap simulation with unchanged rainfall and slope; before/after priority comparisons with clearly described assumptions.
5. Equal-cost budget shortlisting that ranks complete-data zones by priority, caps allocation to the available budget and exports the selected zones. This is a heuristic, not an optimal cost-benefit model.
6. Private scenario records with source data snapshots, scoring version, field notes and self-reported draft / field review / verified status.
7. GitHub Pages build/deploy workflow and relative asset paths plus hash navigation for project subpaths.
8. Editable Figma overview/account designs: https://www.figma.com/design/8eYuA3PG4OVCd2p6x6DXrH

## What remains before live use

New Supabase project creation, schema application, Auth redirect configuration, live cross-user RLS verification, a target GitHub repository, Pages configuration and deployment verification. No hosted URL or completed live authentication is claimed.

## Further innovation, in priority order

| Extension | Why it matters | Evidence needed |
|---|---|---|
| Dated field observations | Links recommendations to ground truth | Site ID, timestamp, method, observer and consent where needed |
| Validated remote-sensing inputs | Moves beyond synthetic examples | Provenance, acquisition date, spatial resolution, cloud quality and normalization |
| Intervention cost-benefit optimization | Allocates limited funds to achievable gains | Local costs, area, expected benefits and feasibility constraints |
| Spatial/temporal evaluation | Reduces misleading random-split results | Geographic holdouts, later-period observations and independent labels |
| Uncertainty and missing-data sensitivity | Shows how fragile each ranking is | Calibration dataset, confidence intervals and weight-sensitivity runs |
| Outcome monitoring | Tests whether interventions work | Baseline and follow-up measurements; appropriate comparison areas |
| Expert review workflow | Separates owner notes from formal validation | Organization membership, reviewer authorization, immutable review history |

These extensions are proposed research work, not features represented as already implemented. Avoid claiming novelty or a validated AI restoration system until comparisons against prior work and real outcomes are available.
