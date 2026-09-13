# Data Source & Modelling Note

The included `data/projects.csv` is carried forward from the supplied Green Dashboard prototype.

It contains project ID, project name, ministry, sector, state, original cost, revised cost, expenditure and physical progress.

To demonstrate predictive monitoring despite the limited snapshot, the backend derives additional demo features deterministically from the supplied fields and project ID. These are clearly labelled in the UI and API as derived/demo features.

For production:
1. Ingest monthly project snapshots from authorised PAIMANA/OCMS sources.
2. Preserve historical versions by project and reporting month.
3. Use only features known at the prediction cut-off.
4. Define future-event labels.
5. Compare conventional statistical methods with ML.
6. Report time-based validation, precision/recall for early warnings, calibration and lead time.
